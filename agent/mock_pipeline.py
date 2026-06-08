"""Mock pipeline for running perpetual-scholar-agent without ML dependencies.

This module provides a complete pipeline implementation using mock components
for LLM, Docker, FAISS, etc. allowing the agent to run in environments without
heavy ML dependencies.

Usage:
    python -m agent.mock_pipeline
"""

import logging
import random
import time
from datetime import datetime, timezone
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def run_mock_pipeline(source: str = "all") -> Dict[str, Any]:
    """Execute one full mock pipeline cycle.

    This simulates the real pipeline but uses mock components for:
    - LLM backends (Ollama, Claude, OpenAI)
    - Docker sandbox execution
    - FAISS vector search
    - RL policy decisions
    - LoRA fine-tuning

    Args:
        source: Ingestion source — "arxiv", "github", "rss", or "all".

    Returns:
        Dictionary with pipeline results (matches real pipeline structure).
    """
    from agent.mock_mode import (
        MockLLMBackend, MockDockerSandbox, MockFAISSIndex,
        MockRLPolicy, is_mock_mode_enabled
    )

    start_time = time.time()
    logger.info("=" * 70)
    logger.info("Starting MOCK pipeline cycle")
    logger.info("=" * 70)

    # Mock ingestion step
    logger.info("[Step 1/6] Ingestion (mock)")
    papers = _mock_ingestion(source)
    logger.info(f"  Found {len(papers)} items")

    # Mock deduplication step
    logger.info("[Step 2/6] Deduplication (mock)")
    unique_papers = papers[:max(1, len(papers) - 1)]
    logger.info(f"  {len(unique_papers)} unique items")

    # Mock summarization step
    logger.info("[Step 3/6] Summarization (mock)")
    llm = MockLLMBackend()
    summaries = []
    for i, paper in enumerate(unique_papers):
        summary = llm._mock_summary()
        summaries.append({
            "paper_id": f"mock_paper_{i}",
            "summary": summary,
            "domain_score": random.uniform(0.5, 0.9)
        })
    logger.info(f"  Generated {len(summaries)} summaries")

    # Mock code generation step
    logger.info("[Step 4/6] Code generation (mock)")
    benchmark_codes = []
    for i, summary in enumerate(summaries):
        code = llm._mock_code()
        benchmark_codes.append({
            "summary_id": f"summary_{i}",
            "code": code,
            "language": "python"
        })
    logger.info(f"  Generated {len(benchmark_codes)} benchmark codes")

    # Mock sandbox execution step
    logger.info("[Step 5/6] Sandbox execution (mock)")
    sandbox = MockDockerSandbox()
    results = []
    for i, code_item in enumerate(benchmark_codes):
        result = sandbox.run_code(code_item["code"])
        results.append({
            "code_id": f"code_{i}",
            "result": result
        })
    successful_results = [r for r in results if r["result"].success]
    logger.info(f"  {len(successful_results)}/{len(results)} experiments succeeded")

    # Mock reward calculation step
    logger.info("[Step 6/6] Reward computation (mock)")
    rewards = []
    for result in successful_results:
        reward = random.uniform(0.3, 0.8)  # Mock positive rewards
        rewards.append(reward)
    avg_reward = sum(rewards) / len(rewards) if rewards else 0.0

    # Mock lesson storage
    lessons_stored = len([r for r in rewards if r > 0.5])
    logger.info(f"  Average reward: {avg_reward:.3f}")
    logger.info(f"  Lessons to store: {lessons_stored}")

    total_time = time.time() - start_time

    result = {
        "papers_processed": len(papers),
        "papers_filtered": len(papers) - len(unique_papers),
        "experiments_run": len(results),
        "experiments_failed": len(results) - len(successful_results),
        "lessons_stored": lessons_stored,
        "lessons_discarded": len(rewards) - lessons_stored,
        "avg_reward": avg_reward,
        "total_time_seconds": total_time,
        "mock_mode": True,
        "source": source,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    logger.info("=" * 70)
    logger.info("Mock pipeline complete!")
    logger.info(f"  Papers: {result['papers_processed']}, "
               f"Experiments: {result['experiments_run']}, "
               f"Lessons: {result['lessons_stored']}")
    logger.info(f"  Avg Reward: {result['avg_reward']:.3f}")
    logger.info("=" * 70)

    return result


def _mock_ingestion(source: str) -> List[Dict[str, Any]]:
    """Mock ingestion step.

    Returns mock papers/repos/RSS items based on source.
    """
    items = []

    if source in ["all", "arxiv"]:
        # Mock arXiv papers
        for i in range(3):
            items.append({
                "id": f"arxiv_{i}",
                "source": "arxiv",
                "title": f"Mock Paper {i}: Advanced ML Technique",
                "authors": ["Author A", "Author B"],
                "summary": f"A novel approach to machine learning problem {i}",
                "url": f"https://arxiv.org/abs/2401.{i:05d}",
                "published": datetime.now(timezone.utc).isoformat()
            })

    if source in ["all", "github"]:
        # Mock GitHub trending repos
        for i in range(2):
            items.append({
                "id": f"github_{i}",
                "source": "github",
                "title": f"Mock Repository {i}",
                "full_name": f"user/mock-repo-{i}",
                "description": f"A fast library for optimization {i}",
                "stars": 1000 + i * 100,
                "language": "Python",
                "url": f"https://github.com/user/mock-repo-{i}"
            })

    if source in ["all", "rss"]:
        # Mock RSS feed items
        items.append({
            "id": "rss_1",
            "source": "rss",
            "title": "Mock RSS Article",
            "summary": "Latest trends in database optimization",
            "url": "https://example.com/article",
            "published": datetime.now(timezone.utc).isoformat()
        })

    return items


def main():
    """Entry point for mock pipeline execution."""
    import sys
    import argparse

    parser = argparse.ArgumentParser(
        description="Run mock pipeline (no ML dependencies)"
    )
    parser.add_argument(
        "--source", type=str, default="all",
        choices=["arxiv", "github", "rss", "all"],
        help="Ingestion source to use"
    )
    args = parser.parse_args()

    try:
        result = run_mock_pipeline(source=args.source)
        print(f"\n{'='*70}")
        print(f"Mock Cycle Complete:")
        print(f"  Papers processed: {result['papers_processed']}")
        print(f"  Experiments run: {result['experiments_run']}")
        print(f"  Lessons stored: {result['lessons_stored']}")
        print(f"  Avg reward: {result['avg_reward']:.3f}")
        print(f"  Time: {result['total_time_seconds']:.2f}s")
        print(f"{'='*70}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Mock pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
