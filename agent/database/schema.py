"""perpetual-scholar-agent — SQLite schema definition and initialization."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Optional, Tuple

from agent.config.settings import settings


SCHEMA_SQL = """
-- ============================================================================
-- Table: seen_items
-- Tracks every ingested item to prevent re-processing (deduplication).
-- ============================================================================
CREATE TABLE IF NOT EXISTS seen_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    source        TEXT NOT NULL,          -- 'arxiv' | 'github' | 'rss'
    source_id     TEXT NOT NULL,          -- arXiv ID, GitHub repo full_name, RSS URL hash
    title         TEXT NOT NULL,
    url           TEXT NOT NULL,
    content_hash  TEXT NOT NULL,          -- SHA-256 of raw content for exact dedup
    embedded_at   TEXT,                   -- ISO-8601 timestamp when embedding was computed
    priority_score REAL DEFAULT 0.0,     -- cosine similarity to DOMAIN_FOCUS embedding
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE(source, source_id)
);

CREATE INDEX IF NOT EXISTS idx_seen_items_source ON seen_items(source);
CREATE INDEX IF NOT EXISTS idx_seen_items_hash ON seen_items(content_hash);

-- ============================================================================
-- Table: experiments
-- Tracks every sandbox experiment: paper → code generation → benchmark.
-- ============================================================================
CREATE TABLE IF NOT EXISTS experiments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    source_item_id  INTEGER NOT NULL,     -- FK to seen_items.id
    technique_name  TEXT,                  -- extracted by summarizer
    generated_code  TEXT,                  -- full Python benchmark code
    sandbox_stdout  TEXT,                  -- raw Docker container stdout
    sandbox_exit_code INTEGER,            -- 0 = success
    ops_per_sec     REAL,                 -- throughput benchmark result
    latency_p50_us REAL,                  -- p50 latency in microseconds
    latency_p99_us REAL,                  -- p99 latency in microseconds
    memory_peak_mb  REAL,                 -- peak memory usage in MB
    baseline_ops_per_sec REAL,            -- baseline throughput for comparison
    reward          REAL,                 -- computed reward: (new - baseline) / baseline
    reward_details  TEXT,                 -- JSON: {benchmark_reward, llm_judge_score, combined_reward}
    status          TEXT NOT NULL DEFAULT 'pending',  -- pending | running | success | failed | timeout
    error_message   TEXT,                 -- error details if status = failed
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    completed_at    TEXT,
    FOREIGN KEY (source_item_id) REFERENCES seen_items(id)
);

CREATE INDEX IF NOT EXISTS idx_experiments_status ON experiments(status);
CREATE INDEX IF NOT EXISTS idx_experiments_reward ON experiments(reward);

-- ============================================================================
-- Table: lessons
-- Verified lessons stored after successful experiments with positive reward.
-- These feed the FAISS index and LoRA fine-tuning.
-- ============================================================================
CREATE TABLE IF NOT EXISTS lessons (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id   INTEGER NOT NULL,     -- FK to experiments.id
    technique_name  TEXT NOT NULL,
    problem_desc    TEXT,                  -- what problem does this technique solve?
    algorithm_desc  TEXT,                  -- algorithm description from paper summary
    pseudocode      TEXT,                  -- pseudocode extracted from paper
    verified_code   TEXT NOT NULL,          -- benchmark-verified Python implementation
    ops_per_sec     REAL NOT NULL,         -- measured throughput
    baseline_ops_per_sec REAL NOT NULL,    -- baseline throughput it beat
    improvement_pct REAL NOT NULL,          -- (new - baseline) / baseline * 100
    reward          REAL NOT NULL,         -- final reward score
    source_url      TEXT,                  -- original paper / repo URL
    source_title    TEXT,                  -- original paper / repo title
    embedding_id    INTEGER,               -- row ID in FAISS index (for vector lookup)
    is_used_in_lora INTEGER NOT NULL DEFAULT 0,  -- 1 if included in a LoRA training set
    created_at      TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_lessons_reward ON lessons(reward DESC);
CREATE INDEX IF NOT EXISTS idx_lessons_technique ON lessons(technique_name);
CREATE INDEX IF NOT EXISTS idx_lessons_is_used_in_lora ON lessons(is_used_in_lora);

-- ============================================================================
-- Table: finetune_runs
-- Tracks LoRA fine-tuning runs for audit trail.
-- ============================================================================
CREATE TABLE IF NOT EXISTS finetune_runs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    adapter_version   TEXT NOT NULL,       -- e.g. "v3"
    num_lessons_used  INTEGER NOT NULL,    -- how many verified lessons were in the training set
    train_loss        REAL,                -- final training loss
    eval_loss          REAL,               -- final eval loss
    training_duration_sec REAL,            -- wall-clock seconds
    adapter_path       TEXT NOT NULL,       -- path to saved adapter directory
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- ============================================================================
-- Table: rl_policy_checkpoints
-- Tracks PPO policy checkpoints.
-- ============================================================================
CREATE TABLE IF NOT EXISTS rl_policy_checkpoints (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    episode       INTEGER NOT NULL,        -- training episode number
    avg_reward    REAL,                     -- average reward over last N episodes
    checkpoint_path TEXT NOT NULL,           -- path to saved policy file
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- ============================================================================
-- Table: metrics_history
-- Time-series metrics for monitoring and dashboard.
-- ============================================================================
CREATE TABLE IF NOT EXISTS metrics_history (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name   TEXT NOT NULL,            -- e.g. 'papers_processed', 'experiments_run', 'avg_reward'
    metric_value  REAL NOT NULL,
    tags          TEXT,                     -- JSON: arbitrary tags for filtering
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics_history(metric_name, created_at);
"""


def init_db(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Create or open the SQLite database and ensure all tables exist.

    Args:
        db_path: Path to the .db file. Defaults to settings.data_dir / 'psa.db'.

    Returns:
        sqlite3.Connection with WAL mode enabled.
    """
    if db_path is None:
        db_path = settings.data_dir / "psa.db"

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get a new connection to the database (for use in async contexts)."""
    if db_path is None:
        db_path = settings.data_dir / "psa.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


if __name__ == "__main__":
    conn = init_db()
    print(f"Database initialized at {settings.data_dir / 'psa.db'}")
    # Verify tables
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables created: {tables}")
    conn.close()
