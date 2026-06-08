"""Reasoning pipeline: lesson retrieval via FAISS top-k search for few-shot context."""
from __future__ import annotations

import logging
from typing import List, Optional

import numpy as np

from agent.config.settings import settings
from agent.vectorstore.faiss_index import FAISSLessonIndex
from agent.database.schema import get_connection

logger = logging.getLogger(__name__)


def retrieve_lessons(
    query_text: str,
    top_k: int = 3,
    min_reward: float = 0.05,
) -> List[dict]:
    """Retrieve the top-k most relevant verified lessons for a given query.

    Uses FAISS vector similarity search to find lessons whose embeddings are
    closest to the query, then enriches them with full lesson data from SQLite.

    Args:
        query_text: Natural language query (e.g. technique name + problem description).
        top_k: Number of lessons to retrieve.
        min_reward: Minimum reward score to include a lesson.

    Returns:
        List of lesson dicts with keys: id, technique_name, verified_code,
        improvement_pct, reward, problem_desc, algorithm_desc.
    """
    import sqlite3

    from agent.ingestion.embedder import embed_text

    db_path = str(settings.data_dir / "psa.db")

    query_embedding = embed_text(query_text)

    faiss_idx = FAISSLessonIndex(
        dimension=settings.embedding_dimension,
        index_dir=settings.data_dir,
    )
    faiss_idx._ensure_index()

    if faiss_idx.total_vectors == 0:
        logger.info("no_lessons_in_faiss", extra={"message": "Returning empty context"})
        return []

    search_results = faiss_idx.search(query_embedding, top_k=top_k * 2)

    if not search_results:
        return []

    lesson_ids = [lesson_db_id for lesson_db_id, distance in search_results]

    conn = get_connection(db_path)
    try:
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" * len(lesson_ids))
        cursor = conn.execute(
            f"""SELECT id, technique_name, problem_desc, algorithm_desc, pseudocode,
                       verified_code, ops_per_sec, baseline_ops_per_sec,
                       improvement_pct, reward, source_url, source_title
                FROM lessons
                WHERE id IN ({placeholders}) AND reward >= ?
                ORDER BY reward DESC
                LIMIT ?""",
            (*lesson_ids, min_reward, top_k),
        )
        lessons = [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()

    logger.info("lessons_retrieved", extra={
        "query": query_text[:50],
        "count": len(lessons),
        "top_k": top_k,
    })
    return lessons


def format_lessons_for_prompt(lessons: List[dict], max_snippet_length: int = 500) -> str:
    """Format retrieved lessons into a prompt-friendly string for few-shot context.

    Args:
        lessons: List of lesson dicts from retrieve_lessons.
        max_snippet_length: Maximum code snippet length per lesson.

    Returns:
        Formatted string suitable for inclusion in an LLM prompt.
    """
    if not lessons:
        return ""

    parts = []
    for i, lesson in enumerate(lessons, 1):
        code_snippet = lesson.get("verified_code", "")
        if len(code_snippet) > max_snippet_length:
            code_snippet = code_snippet[:max_snippet_length] + "\n# ... (truncated)"

        parts.append(
            f"--- Verified Technique #{i} ---\n"
            f"Technique: {lesson.get('technique_name', 'Unknown')}\n"
            f"Problem: {lesson.get('problem_desc', 'N/A')[:200]}\n"
            f"Improvement: +{lesson.get('improvement_pct', 0):.1f}% "
            f"({lesson.get('baseline_ops_per_sec', 0):.0f} → "
            f"{lesson.get('ops_per_sec', 0):.0f} ops/s)\n"
            f"Code:\n{code_snippet}\n"
        )

    return "\n".join(parts)
