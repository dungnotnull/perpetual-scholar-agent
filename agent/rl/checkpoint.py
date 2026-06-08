"""RL: Checkpoint save/load utilities."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)

CHECKPOINT_DIR = "rl_policy"


def save_checkpoint_metadata(
    episode: int,
    avg_reward: float,
    checkpoint_path: str,
    db_path: Optional[str] = None,
) -> None:
    """Save checkpoint metadata to the database.

    Args:
        episode: Training episode number.
        avg_reward: Average reward over recent episodes.
        checkpoint_path: Path to the saved policy file.
        db_path: Path to SQLite database.
    """
    import aiosqlite
    import asyncio

    async def _save():
        nonlocal db_path
        if db_path is None:
            db_path = str(settings.data_dir / "psa.db")

        async with aiosqlite.connect(db_path) as conn:
            await conn.execute(
                """INSERT INTO rl_policy_checkpoints
                   (episode, avg_reward, checkpoint_path)
                   VALUES (?, ?, ?)""",
                (episode, avg_reward, checkpoint_path),
            )
            await conn.commit()

    asyncio.run(_save())
    logger.info(f"Saved checkpoint metadata: episode={episode}, avg_reward={avg_reward:.4f}")


def get_latest_checkpoint(models_dir: Optional[Path] = None) -> Optional[Path]:
    """Find the latest RL policy checkpoint.

    Args:
        models_dir: Directory containing model checkpoints.

    Returns:
        Path to latest checkpoint zip file, or None.
    """
    if models_dir is None:
        models_dir = settings.models_dir

    checkpoint_dir = models_dir / CHECKPOINT_DIR
    if not checkpoint_dir.exists():
        return None

    checkpoints = sorted(checkpoint_dir.glob("ppo_policy_*.zip"))
    return checkpoints[-1] if checkpoints else None
