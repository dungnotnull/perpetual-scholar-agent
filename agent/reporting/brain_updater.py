"""Reporting: SECOND-KNOWLEDGE-BRAIN.md auto-updater."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiosqlite

from agent.config.settings import settings

logger = logging.getLogger(__name__)


async def update_knowledge_brain(
    brain_path: Optional[str] = None,
    db_path: Optional[str] = None,
    top_n: int = 10,
) -> str:
    """Append new verified lessons to SECOND-KNOWLEDGE-BRAIN.md.

    This is called weekly by the scheduler to update the Knowledge Update Log
    section of the brain file.

    Args:
        brain_path: Path to SECOND-KNOWLEDGE-BRAIN.md.
        db_path: Path to SQLite database.
        top_n: Number of top lessons to include.

    Returns:
        The appended content string.
    """
    if brain_path is None:
        brain_path = str(Path(__file__).parent.parent.parent / "SECOND-KNOWLEDGE-BRAIN.md")
    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    now = datetime.now(timezone.utc)
    week_num = now.isocalendar()[1]

    # Fetch top lessons from the past week
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(
            """SELECT technique_name, problem_desc, verified_code, ops_per_sec,
                      baseline_ops_per_sec, improvement_pct, reward, source_url, source_title
               FROM lessons
               WHERE created_at >= datetime('now', '-7 days')
               ORDER BY reward DESC
               LIMIT ?""",
            (top_n,),
        )
        lessons = [dict(r) for r in await cursor.fetchall()]

        # Count total new lessons
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM lessons WHERE created_at >= datetime('now', '-7 days')"
        )
        total_new = (await cursor.fetchone())[0]

    if not lessons:
        logger.info("No new lessons this week — skipping brain update")
        return ""

    # Best lesson
    best = lessons[0]

    # Build update entry
    lines = [
        f"\n### [{now.strftime('%Y-%m-%d')}] Week {week_num} Update",
        "",
        f"**New Lessons Verified**: {total_new}",
        f"**Top Technique This Week**: {best['technique_name']} (reward: {best['reward']:.2f})",
        f"**Paper Source**: {best.get('source_title', 'N/A')} — {best.get('source_url', 'N/A')}",
        f"**Benchmark Result**: {best['baseline_ops_per_sec']:.2f} → {best['ops_per_sec']:.2f} ops/s (+{best['improvement_pct']:.1f}%)",
        f"**Summary**: {best.get('problem_desc', 'N/A')[:200]}",
        "",
        "| # | Technique | Improvement | Reward | Source |",
        "|---|-----------|-------------|--------|--------|",
    ]

    for i, lesson in enumerate(lessons, 1):
        lines.append(
            f"| {i} | {lesson['technique_name'][:35]} | "
            f"+{lesson['improvement_pct']:.1f}% | "
            f"{lesson['reward']:.3f} | "
            f"[link]({lesson.get('source_url', '#')}) |"
        )

    lines.append("")

    update_content = "\n".join(lines)

    # Append to the brain file
    brain_file = Path(brain_path)
    if brain_file.exists():
        with open(brain_file, "a", encoding="utf-8") as f:
            f.write(update_content)
        logger.info(f"Appended {len(lessons)} lessons to {brain_path}")
    else:
        logger.warning(f"Brain file not found at {brain_path} — creating new file")
        brain_file.parent.mkdir(parents=True, exist_ok=True)
        with open(brain_file, "w", encoding="utf-8") as f:
            f.write(update_content)

    return update_content
