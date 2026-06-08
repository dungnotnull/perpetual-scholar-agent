"""Orchestrator: single pipeline cycle — ingestion → reasoning → sandbox → reward → storage.

This is the core E2E pipeline that runs once per trigger. Every step has proper
error handling, structured logging, circuit breaker protection, and metric recording.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional

from agent.config.settings import settings
from agent.database.schema import init_db
from agent.ingestion.arxiv_fetcher import fetch_arxiv_papers, PaperItem
from agent.ingestion.github_fetcher import fetch_github_trending, GitHubItem
from agent.ingestion.rss_fetcher import fetch_rss_feeds, RSSItem
from agent.ingestion.deduplicator import deduplicate_items
from agent.ingestion.embedder import compute_domain_focus_embedding, score_items, embed_text
from agent.reasoning.summarizer import summarize_paper
from agent.reasoning.code_generator import generate_benchmark_code
from agent.reasoning.lesson_retriever import retrieve_lessons, format_lessons_for_prompt
from agent.sandbox.executor import SandboxExecutor
from agent.sandbox.benchmark_harness import parse_benchmark_json, extract_metrics
from agent.sandbox.resource_limits import validate_benchmark_result, DEFAULT_LIMITS
from agent.reward.calculator import compute_reward
from agent.reward.lesson_writer import store_lesson
from agent.monitoring.metrics import start_session, get_current_session, record_metric
from agent.resilience import sandbox_circuit_breaker

logger = logging.getLogger(__name__)


async def run_once(source: str = "all") -> Dict:
    """Execute one full pipeline cycle.

    Pipeline steps:
      1. Ingestion — fetch papers/repos/RSS
      2. Deduplication — filter already-seen items
      3. Embedding & prioritization — score items by domain relevance
      4. Summarization — extract technique details from each item
      5. Code generation — create runnable benchmarks
      6. Sandbox execution — run code in isolated Docker container
      7. Reward computation — compare against baseline
      8. Lesson storage — store verified lessons to SQLite + FAISS

    Args:
        source: Ingestion source — "arxiv", "github", "rss", or "all".

    Returns:
        Dict with cycle statistics.
    """
    session = start_session()
    logger.info(
        "pipeline_cycle_started",
        extra={"source": source, "session_id": session.session_id},
    )

    results = {
        "session_id": session.session_id,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "papers_fetched": 0,
        "novel_items": 0,
        "experiments_run": 0,
        "experiments_succeeded": 0,
        "experiments_failed": 0,
        "lessons_stored": 0,
        "total_reward": 0.0,
        "avg_reward": 0.0,
        "best_reward": -1.0,
        "best_technique": "",
        "errors": [],
    }

    # ── Step 1: Initialize ──────────────────────────────────────────────────
    try:
        conn = init_db()
        conn.close()
    except Exception as e:
        logger.error("database_init_failed", extra={"error": str(e)})
        results["errors"].append(f"database_init: {e}")
        return results

    # ── Step 2: Ingestion ────────────────────────────────────────────────────
    all_items: list = []

    if source in ("arxiv", "all"):
        try:
            papers = fetch_arxiv_papers()
            all_items.extend(papers)
            logger.info("arxiv_fetch_complete", extra={"count": len(papers)})
        except Exception as e:
            logger.error("arxiv_fetch_failed", extra={"error": str(e)})
            results["errors"].append(f"arxiv: {e}")

    if source in ("github", "all"):
        try:
            repos = fetch_github_trending()
            all_items.extend(repos)
            logger.info("github_fetch_complete", extra={"count": len(repos)})
        except Exception as e:
            logger.error("github_fetch_failed", extra={"error": str(e)})
            results["errors"].append(f"github: {e}")

    if source in ("rss", "all"):
        try:
            rss_items = fetch_rss_feeds()
            all_items.extend(rss_items)
            logger.info("rss_fetch_complete", extra={"count": len(rss_items)})
        except Exception as e:
            logger.error("rss_fetch_failed", extra={"error": str(e)})
            results["errors"].append(f"rss: {e}")

    session.papers_fetched = len(all_items)
    results["papers_fetched"] = len(all_items)

    # ── Step 3: Deduplication ────────────────────────────────────────────────
    try:
        novel_items = await deduplicate_items(all_items)
        session.novel_items = len(novel_items)
        results["novel_items"] = len(novel_items)
    except Exception as e:
        logger.error("deduplication_failed", extra={"error": str(e)})
        results["errors"].append(f"dedup: {e}")
        novel_items = all_items  # proceed with all items if dedup fails

    if not novel_items:
        logger.info("no_novel_items", extra={"message": "Cycle complete — no new items"})
        return results

    # ── Step 4: Embedding & Prioritization ───────────────────────────────────
    try:
        domain_embedding = compute_domain_focus_embedding()
        scored_items = score_items(novel_items, domain_embedding)
    except Exception as e:
        logger.warning("scoring_failed_using_unsorted", extra={"error": str(e)})
        scored_items = novel_items

    # ── Step 5-9: Process top items ──────────────────────────────────────────
    max_items = min(5, len(scored_items))
    rewards = []

    # Check circuit breaker before starting experiments
    if sandbox_circuit_breaker.is_open:
        logger.warning(
            "circuit_breaker_open",
            extra={"message": "Sandbox failure rate too high — pausing experiments"},
        )
        results["errors"].append("circuit_breaker_open")

    executor = SandboxExecutor()
    try:
        if not executor.healthcheck():
            logger.warning("sandbox_unavailable", extra={"message": "Docker image not available"})

        for item in scored_items[:max_items]:
            # Skip processing if circuit breaker is open
            if sandbox_circuit_breaker.is_open:
                logger.warning("skipping_experiment_circuit_breaker")
                break

            logger.info(
                "processing_item",
                extra={
                    "title": item.title[:80],
                    "priority": getattr(item, "priority_score", 0),
                },
            )

            try:
                result = await _process_single_item(item, executor)
                if result is not None:
                    session.experiments_run += 1
                    results["experiments_run"] += 1

                    if result.get("success"):
                        session.experiments_succeeded += 1
                        results["experiments_succeeded"] += 1
                        rewards.append(result["reward"])
                        if result.get("lesson_id"):
                            session.lessons_stored += 1
                            results["lessons_stored"] += 1
                            session.best_reward = max(session.best_reward, result["reward"])
                            session.best_technique = result.get("technique_name", "")
                    else:
                        session.experiments_failed += 1
                        results["experiments_failed"] += 1
                        sandbox_circuit_breaker.record_failure()
                else:
                    sandbox_circuit_breaker.record_failure()

            except Exception as e:
                logger.error("item_processing_failed", extra={"error": str(e), "title": item.title[:50]})
                results["errors"].append(str(e))
                sandbox_circuit_breaker.record_failure()
                continue

    finally:
        executor.cleanup_all()

    # ── Aggregate results ───────────────────────────────────────────────────
    if rewards:
        session.avg_reward = sum(rewards) / len(rewards)
        session.best_reward = max(rewards)

    results["avg_reward"] = session.avg_reward
    results["best_reward"] = session.best_reward
    results["best_technique"] = session.best_technique

    await record_metric("papers_fetched", results["papers_fetched"])
    await record_metric("experiments_run", results["experiments_run"])
    await record_metric("lessons_stored", results["lessons_stored"])
    await record_metric("avg_reward", results["avg_reward"])

    logger.info(
        "pipeline_cycle_complete",
        extra={
            "experiments": results["experiments_run"],
            "lessons": results["lessons_stored"],
            "avg_reward": results["avg_reward"],
            "errors": len(results["errors"]),
        },
    )

    return results


async def _process_single_item(item, executor: SandboxExecutor) -> Optional[Dict]:
    """Process a single ingested item through the full pipeline.

    Returns a dict with success/reward info, or None if the item should be skipped.
    """
    abstract = getattr(item, "abstract", "") or getattr(item, "description", "")

    # Step 5: Summarize
    summary = await summarize_paper(title=item.title, abstract=abstract, url=item.url)
    if summary.confidence < 0.3:
        logger.info("low_confidence_skip", extra={"technique": summary.technique_name})
        return None

    # Retrieve relevant lessons for few-shot context
    context_lessons = retrieve_lessons(
        query_text=f"{summary.technique_name} {summary.problem_solved}",
        top_k=3,
    )
    context_str = format_lessons_for_prompt(context_lessons) if context_lessons else ""

    # Step 6: Generate code
    code = await generate_benchmark_code(
        technique_name=summary.technique_name,
        problem_solved=summary.problem_solved,
        algorithm_description=summary.algorithm_description,
        pseudocode=summary.pseudocode,
        context_lessons=context_str.split("\n")[:3] if context_str else None,
    )

    if not code or len(code.strip()) < 20:
        logger.warning("code_generation_too_short", extra={"technique": summary.technique_name})
        return None

    # Step 7: Benchmark
    sandbox_result = executor.execute(code)
    is_valid, reason = validate_benchmark_result(
        sandbox_result["exit_code"],
        sandbox_result["stdout"],
        sandbox_result["stderr"],
        sandbox_result["timed_out"],
    )

    if not is_valid:
        logger.warning("benchmark_invalid", extra={"reason": reason})
        sandbox_circuit_breaker.record_failure()
        return {"success": False, "reason": reason}

    sandbox_circuit_breaker.record_success()

    # Parse benchmark results
    benchmark_data = sandbox_result.get("benchmark_results") or {}
    parsed_benchmarks = parse_benchmark_json(benchmark_data) if benchmark_data else []
    metrics = extract_metrics(parsed_benchmarks)

    if not metrics.get("baseline_found") or not metrics.get("technique_found"):
        logger.warning("missing_baseline_or_technique_in_benchmark")
        return {"success": False, "reason": "missing_baseline_or_technique"}

    # Step 8: Compute reward
    reward_result = compute_reward(
        new_metric=metrics["ops_per_sec"],
        baseline_metric=metrics["baseline_ops_per_sec"],
    )

    # Step 9: Store lesson if positive
    if reward_result.is_positive:
        lesson_embedding = embed_text(f"{summary.technique_name} {summary.problem_solved} {summary.algorithm_description}")
        lesson_id = await store_lesson(
            experiment_id=0,
            technique_name=summary.technique_name,
            problem_desc=summary.problem_solved,
            algorithm_desc=summary.algorithm_description,
            pseudocode=summary.pseudocode,
            verified_code=code,
            ops_per_sec=metrics["ops_per_sec"],
            baseline_ops_per_sec=metrics["baseline_ops_per_sec"],
            improvement_pct=metrics["improvement_pct"],
            reward=reward_result.combined_reward,
            source_url=item.url,
            source_title=item.title,
            embedding=lesson_embedding,
        )

        logger.info(
            "lesson_stored",
            extra={
                "technique": summary.technique_name,
                "improvement": f"+{metrics['improvement_pct']:.1f}%",
                "reward": f"{reward_result.combined_reward:.3f}",
                "lesson_id": lesson_id,
            },
        )

        return {
            "success": True,
            "reward": reward_result.combined_reward,
            "lesson_id": lesson_id,
            "technique_name": summary.technique_name,
        }

    return {"success": False, "reason": f"reward_not_positive: {reward_result.combined_reward:.3f}"}
