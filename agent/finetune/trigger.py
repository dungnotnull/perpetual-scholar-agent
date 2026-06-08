"""Finetune: trigger logic for auto-fine-tuning."""
from __future__ import annotations

import logging
from pathlib import Path

from agent.config.settings import settings
from agent.finetune.dataset_exporter import count_untrained_lessons

logger = logging.getLogger(__name__)


def should_finetune(db_path: str | None = None) -> tuple[bool, str]:
    """Check if fine-tuning should be triggered.

    Triggers when either:
    - Untrained lessons >= LORA_TRIGGER_LESSON_COUNT (default 50), OR
    - Days since last fine-tune >= LORA_TRIGGER_DAYS (default 7)

    Args:
        db_path: Path to SQLite database.

    Returns:
        Tuple of (should_trigger: bool, reason: str).
    """
    import sqlite3
    import datetime

    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    # Check lesson count threshold
    untrained_count = count_untrained_lessons(db_path)
    if untrained_count >= settings.lora_trigger_lesson_count:
        return True, f"Lesson threshold reached: {untrained_count} >= {settings.lora_trigger_lesson_count}"

    # Check time threshold
    conn = sqlite3.connect(db_path)
    cursor = conn.execute(
        "SELECT created_at FROM finetune_runs ORDER BY created_at DESC LIMIT 1"
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        # Never fine-tuned — check if we have any lessons at all
        if untrained_count > 0:
            return True, "First fine-tuning run (no previous runs)"
        return False, "No lessons available for fine-tuning"

    last_run = datetime.datetime.fromisoformat(row[0].replace("Z", "+00:00"))
    days_since = (datetime.datetime.now(datetime.timezone.utc) - last_run).days

    if days_since >= settings.lora_trigger_days:
        return True, f"Time threshold reached: {days_since} days >= {settings.lora_trigger_days}"

    return False, f"Thresholds not met: {untrained_count} lessons, {days_since} days since last run"


async def trigger_finetune_if_needed() -> bool:
    """Check trigger conditions and run fine-tuning if needed.

    Returns:
        True if fine-tuning was triggered, False otherwise.
    """
    should, reason = should_finetune()

    if not should:
        logger.info(f"Fine-tuning not triggered: {reason}")
        return False

    logger.info(f"Triggering fine-tuning: {reason}")

    # Export dataset
    from agent.finetune.dataset_exporter import export_training_dataset
    dataset_path = await export_training_dataset()

    # Check dataset has examples
    from pathlib import Path
    if not Path(dataset_path).exists():
        logger.warning("No dataset exported — skipping fine-tuning")
        return False

    # Run fine-tuning
    from agent.finetune.trainer import run_lora_finetuning
    try:
        adapter_path = run_lora_finetuning(dataset_path=dataset_path)
        logger.info(f"Fine-tuning complete. Adapter saved to: {adapter_path}")
        return True
    except Exception as e:
        logger.error(f"Fine-tuning failed: {e}")
        return False
