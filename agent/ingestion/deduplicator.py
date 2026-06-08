"""Ingestion pipeline: deduplication via SHA-256 content hash."""
from __future__ import annotations

import hashlib
import logging
from typing import List

import aiosqlite

from agent.config.settings import settings

logger = logging.getLogger(__name__)


def compute_content_hash(*parts: str) -> str:
    """Compute SHA-256 hash of concatenated content parts.

    Args:
        *parts: String parts to hash together.

    Returns:
        Hex-encoded SHA-256 hash string.
    """
    content = "\n".join(parts)
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


async def deduplicate_items(items: list, db_path: str | None = None) -> list:
    """Filter out already-seen items by content hash.

    For each item, checks if its content_hash already exists in the seen_items
    table. New items are recorded in the database for future deduplication.

    Args:
        items: List of item objects with .source, .source_id, .title, .url, .content_hash.
        db_path: Path to SQLite database. Defaults to settings.

    Returns:
        List of novel items (not previously seen).
    """
    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    novel_items = []

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("PRAGMA journal_mode=WAL")

        for item in items:
            # Check if content hash exists
            cursor = await conn.execute(
                "SELECT id FROM seen_items WHERE content_hash = ?",
                (item.content_hash,),
            )
            row = await cursor.fetchone()

            if row is None:
                # New item — insert into seen_items
                await conn.execute(
                    """INSERT INTO seen_items (source, source_id, title, url, content_hash)
                       VALUES (?, ?, ?, ?, ?)""",
                    (item.source, item.source_id, item.title, item.url, item.content_hash),
                )
                novel_items.append(item)
            else:
                logger.debug(f"Dedup: skipping {item.source}/{item.source_id} (already seen)")

        await conn.commit()

    logger.info(f"Deduplication: {len(items)} items → {len(novel_items)} novel")
    return novel_items


async def is_seen(source: str, source_id: str, db_path: str | None = None) -> bool:
    """Check if a specific item has been seen before."""
    if db_path is None:
        db_path = str(settings.data_dir / "psa.db")

    async with aiosqlite.connect(db_path) as conn:
        cursor = await conn.execute(
            "SELECT id FROM seen_items WHERE source = ? AND source_id = ?",
            (source, source_id),
        )
        return await cursor.fetchone() is not None
