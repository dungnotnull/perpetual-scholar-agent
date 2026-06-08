"""Reward engine: lesson writer to SQLite + FAISS with structured logging and error handling."""
from __future__ import annotations

import logging
from typing import Optional

import numpy as np

from agent.config.settings import settings
from agent.reward.calculator import RewardResult

logger = logging.getLogger(__name__)


async def store_lesson(
    experiment_id: int,
    technique_name: str,
    problem_desc: str,
    algorithm_desc: str,
    pseudocode: str,
    verified_code: str,
    ops_per_sec: float,
    baseline_ops_per_sec: float,
    improvement_pct: float,
    reward: float,
    source_url: str = "",
    source_title: str = "",
    embedding: Optional[np.ndarray] = None,
) -> int:
    """Store a verified lesson in SQLite and FAISS index.

    Args:
        experiment_id: FK to experiments table.
        technique_name: Name of the technique.
        problem_desc: Problem solved.
        algorithm_desc: Algorithm description.
        pseudocode: Pseudocode from paper summary.
        verified_code: Benchmark-verified Python implementation.
        ops_per_sec: Measured throughput.
        baseline_ops_per_sec: Baseline throughput.
        improvement_pct: Percentage improvement.
        reward: Computed reward score.
        source_url: Original paper/repo URL.
        source_title: Original paper/repo title.
        embedding: Pre-computed embedding vector.

    Returns:
        lesson id from SQLite.
    """
    import aiosqlite

    db_path = str(settings.data_dir / "psa.db")

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("PRAGMA journal_mode=WAL")
        await conn.execute("PRAGMA foreign_keys=ON")

        cursor = await conn.execute(
            """INSERT INTO lessons
               (experiment_id, technique_name, problem_desc, algorithm_desc, pseudocode,
                verified_code, ops_per_sec, baseline_ops_per_sec, improvement_pct,
                reward, source_url, source_title)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (experiment_id, technique_name, problem_desc, algorithm_desc, pseudocode,
             verified_code, ops_per_sec, baseline_ops_per_sec, improvement_pct,
             reward, source_url, source_title),
        )
        lesson_id = cursor.lastrowid

        # Add to FAISS index if embedding provided
        if embedding is not None:
            try:
                from agent.vectorstore.faiss_index import FAISSLessonIndex
                faiss_idx = FAISSLessonIndex(
                    dimension=settings.embedding_dimension,
                    index_dir=settings.data_dir,
                )
                faiss_idx._ensure_index()
                position = faiss_idx.add(embedding, lesson_db_id=lesson_id)
                await conn.execute(
                    "UPDATE lessons SET embedding_id = ? WHERE id = ?",
                    (position, lesson_id),
                )
                faiss_idx.save()
                logger.debug("lesson_embedding_stored", extra={"lesson_id": lesson_id, "faiss_position": position})
            except Exception as e:
                logger.warning("faiss_index_failed", extra={"lesson_id": lesson_id, "error": str(e)})

        await conn.commit()

    logger.info(
        "lesson_stored",
        extra={
            "lesson_id": lesson_id,
            "technique": technique_name,
            "improvement": f"{improvement_pct:.1f}%",
            "reward": f"{reward:.3f}",
        },
    )
    return lesson_id


async def get_top_lessons(limit: int = 10) -> list:
    """Get top lessons ranked by reward score."""
    import aiosqlite

    db_path = str(settings.data_dir / "psa.db")

    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """SELECT id, technique_name, problem_desc, ops_per_sec,
                      baseline_ops_per_sec, improvement_pct, reward, source_url
               FROM lessons
               ORDER BY reward DESC
               LIMIT ?""",
            (limit,),
        )
        rows = await cursor.fetchall()

    return [dict(r) for r in rows]


async def get_lessons_since_last_finetune() -> list:
    """Get lessons not yet used in LoRA training."""
    import aiosqlite

    db_path = str(settings.data_dir / "psa.db")

    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """SELECT * FROM lessons
               WHERE is_used_in_lora = 0
               ORDER BY created_at ASC"""
        )
        rows = await cursor.fetchall()

    return [dict(r) for r in rows]
