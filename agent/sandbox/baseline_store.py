"""Sandbox execution: baseline metric store."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import aiosqlite

from agent.config.settings import settings

logger = logging.getLogger(__name__)


async def get_baseline(
    domain: str = "default",
    db_path: Optional[str] = None,
) -> dict:
    """Get the current baseline metrics for a domain.

    Returns:
        Dict with baseline throughput and latency metrics.
    """
    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.execute(
            """SELECT ops_per_sec, latency_p50_us, latency_p99_us
               FROM experiments
               WHERE status = 'success' AND technique_name IS NULL
               ORDER BY created_at DESC LIMIT 1""",
        )
        row = await cursor.fetchone()

    if row:
        return {
            "ops_per_sec": row[0],
            "latency_p50_us": row[1],
            "latency_p99_us": row[2],
        }
    else:
        # Return default baselines
        return {
            "ops_per_sec": 1.0,  # Will be set after first baseline run
            "latency_p50_us": 0.0,
            "latency_p99_us": 0.0,
        }


async def set_baseline(
    ops_per_sec: float,
    latency_p50_us: float,
    latency_p99_us: float,
    domain: str = "default",
    db_path: Optional[str] = None,
) -> None:
    """Store baseline metrics for a domain."""
    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute(
            """INSERT INTO experiments
               (source_item_id, technique_name, ops_per_sec, latency_p50_us, latency_p99_us, status)
               VALUES (?, NULL, ?, ?, ?, 'success')""",
            (0, ops_per_sec, latency_p50_us, latency_p99_us),
        )
        await conn.commit()

    logger.info(f"Baseline set: {ops_per_sec:.2f} ops/s, p50={latency_p50_us:.1f}us")
