"""Monitoring: metrics tracking for experiments and pipeline."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class SessionMetrics:
    """Tracks metrics for a single pipeline session/cycle."""
    session_id: str = ""
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    papers_fetched: int = 0
    novel_items: int = 0
    experiments_run: int = 0
    experiments_succeeded: int = 0
    experiments_failed: int = 0
    lessons_stored: int = 0
    total_reward: float = 0.0
    avg_reward: float = 0.0
    best_reward: float = -1.0
    best_technique: str = ""
    errors: list = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "papers_fetched": self.papers_fetched,
            "novel_items": self.novel_items,
            "experiments_run": self.experiments_run,
            "experiments_succeeded": self.experiments_succeeded,
            "experiments_failed": self.experiments_failed,
            "lessons_stored": self.lessons_stored,
            "avg_reward": self.avg_reward,
            "best_reward": self.best_reward,
            "best_technique": self.best_technique,
        }


# Global session metrics (singleton)
_current_session: Optional[SessionMetrics] = None


def start_session(session_id: Optional[str] = None) -> SessionMetrics:
    """Start a new metrics tracking session."""
    global _current_session
    import uuid
    _current_session = SessionMetrics(
        session_id=session_id or str(uuid.uuid4())[:8],
    )
    return _current_session


def get_current_session() -> Optional[SessionMetrics]:
    """Get the current session metrics."""
    return _current_session


async def record_metric(name: str, value: float, tags: Optional[Dict] = None) -> None:
    """Record a metric to the database.

    Args:
        name: Metric name (e.g. 'papers_processed', 'avg_reward').
        value: Metric value.
        tags: Optional dict of tags for filtering.
    """
    import json
    import aiosqlite

    db_path = str(settings.data_dir / "psa.db")
    tags_json = json.dumps(tags or {})

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute(
            "INSERT INTO metrics_history (metric_name, metric_value, tags) VALUES (?, ?, ?)",
            (name, value, tags_json),
        )
        await conn.commit()


def get_prometheus_metrics() -> str:
    """Generate Prometheus-format metrics output.

    Returns:
        String in Prometheus exposition format.
    """
    lines = []
    session = get_current_session()

    if session:
        lines.append(f"# HELP psa_papers_fetched Total papers fetched")
        lines.append(f"# TYPE psa_papers_fetched counter")
        lines.append(f"psa_papers_fetched {session.papers_fetched}")

        lines.append(f"# HELP psa_experiments_run Total experiments run")
        lines.append(f"# TYPE psa_experiments_run counter")
        lines.append(f"psa_experiments_run {session.experiments_run}")

        lines.append(f"# HELP psa_experiments_succeeded Experiments that succeeded")
        lines.append(f"# TYPE psa_experiments_succeeded counter")
        lines.append(f"psa_experiments_succeeded {session.experiments_succeeded}")

        lines.append(f"# HELP psa_lessons_stored Total lessons stored")
        lines.append(f"# TYPE psa_lessons_stored counter")
        lines.append(f"psa_lessons_stored {session.lessons_stored}")

        lines.append(f"# HELP psa_avg_reward Average reward this session")
        lines.append(f"# TYPE psa_avg_reward gauge")
        lines.append(f"psa_avg_reward {session.avg_reward:.4f}")

    return "\n".join(lines)
