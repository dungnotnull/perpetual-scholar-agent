"""Finetune: dataset exporter from SQLite to JSONL for LoRA training."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import List, Optional

import aiosqlite

from agent.config.settings import settings

logger = logging.getLogger(__name__)


async def export_training_dataset(
    output_path: Optional[str] = None,
    db_path: Optional[str] = None,
    only_untrained: bool = True,
) -> str:
    """Export verified lessons as a JSONL dataset for LoRA fine-tuning.

    Each line is a JSON object: {"prompt": ..., "completion": ...}

    Args:
        output_path: Path to write the JSONL file.
        db_path: Path to SQLite database.
        only_untrained: Only export lessons not yet used in LoRA training.

    Returns:
        Path to the exported dataset file.
    """
    if output_path is None:
        output_path = str(settings.data_dir / "finetune_dataset.jsonl")
    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    lessons = []
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row

        if only_untrained:
            cursor = await conn.execute(
                """SELECT technique_name, problem_desc, algorithm_desc,
                          pseudocode, verified_code, improvement_pct, reward
                   FROM lessons
                   WHERE is_used_in_lora = 0 AND reward > 0
                   ORDER BY reward DESC"""
            )
        else:
            cursor = await conn.execute(
                """SELECT technique_name, problem_desc, algorithm_desc,
                          pseudocode, verified_code, improvement_pct, reward
                   FROM lessons
                   WHERE reward > 0
                   ORDER BY reward DESC"""
            )
        rows = await cursor.fetchall()
        for row in rows:
            lessons.append(dict(row))

    if not lessons:
        logger.warning("No lessons available for dataset export")
        return output_path

    # Write JSONL
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for lesson in lessons:
            prompt = (
                f"Technique: {lesson['technique_name']}\n"
                f"Problem: {lesson['problem_desc']}\n"
                f"Algorithm: {lesson['algorithm_desc']}\n"
                f"Write a Python implementation with pytest-benchmark."
            )
            completion = lesson["verified_code"]
            f.write(json.dumps({"prompt": prompt, "completion": completion}) + "\n")

    logger.info(f"Exported {len(lessons)} lessons to {output_path}")
    return output_path


def count_untrained_lessons(db_path: Optional[str] = None) -> int:
    """Count lessons not yet used in LoRA training."""
    import sqlite3

    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT COUNT(*) FROM lessons WHERE is_used_in_lora = 0 AND reward > 0"
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count
