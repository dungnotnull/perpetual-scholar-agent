"""Finetune: LoRA adapter management — versioning, symlinks, and cleanup."""
from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


def get_adapter_dir(version: Optional[str] = None) -> Path:
    """Get the directory path for a specific adapter version.

    Args:
        version: Adapter version string (e.g. "v3"). If None, returns latest.

    Returns:
        Path to the adapter directory.
    """
    if version is None:
        latest = settings.models_dir / "lora_adapter_latest"
        if latest.is_symlink():
            return latest.resolve()
        return settings.models_dir / "lora_adapter_latest"

    return settings.models_dir / f"lora_adapter_{version}"


def get_next_version() -> str:
    """Determine the next adapter version number.

    Scans existing adapter directories and increments the highest version.

    Returns:
        Version string like "v1", "v2", etc.
    """
    models_dir = settings.models_dir
    versions = []
    for d in models_dir.glob("lora_adapter_v*"):
        name = d.name
        try:
            num = int(name.split("_v")[1])
            versions.append(num)
        except (ValueError, IndexError):
            continue

    next_num = max(versions, default=0) + 1
    return f"v{next_num}"


def save_adapter_version(source_dir: str, version: Optional[str] = None) -> str:
    """Copy a trained adapter to a versioned directory and update the latest symlink.

    Args:
        source_dir: Path to the directory containing adapter weights (output of SFTTrainer).
        version: Version string. If None, auto-incremented.

    Returns:
        The version string used.
    """
    if version is None:
        version = get_next_version()

    target_dir = settings.models_dir / f"lora_adapter_{version}"

    # Remove existing version if it exists
    if target_dir.exists():
        shutil.rmtree(target_dir)

    # Copy adapter files
    shutil.copytree(source_dir, target_dir)
    logger.info(f"Adapter saved to {target_dir}")

    # Update latest symlink
    latest_link = settings.models_dir / "lora_adapter_latest"
    if latest_link.is_symlink() or latest_link.exists():
        latest_link.unlink()
    latest_link.symlink_to(target_dir)
    logger.info(f"Latest symlink updated -> {target_dir}")

    # Record in database
    _record_adapter_in_db(version, str(target_dir))

    return version


def list_adapter_versions() -> list[dict]:
    """List all saved adapter versions with metadata.

    Returns:
        List of dicts with keys: version, path, size_mb, created_at.
    """
    models_dir = settings.models_dir
    adapters = []

    for d in sorted(models_dir.glob("lora_adapter_v*")):
        name = d.name
        version = name.replace("lora_adapter_", "")

        # Calculate total size
        total_size = sum(f.stat().st_size for f in d.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)

        # Get creation time
        stat = d.stat()
        import datetime
        created_at = datetime.datetime.fromtimestamp(stat.st_ctime).isoformat()

        adapters.append({
            "version": version,
            "path": str(d),
            "size_mb": round(size_mb, 2),
            "created_at": created_at,
        })

    return adapters


def cleanup_old_adapters(keep_last: int = 3) -> list[str]:
    """Remove old adapter versions, keeping only the most recent N.

    Args:
        keep_last: Number of recent adapters to keep.

    Returns:
        List of removed version strings.
    """
    adapters = list_adapter_versions()
    if len(adapters) <= keep_last:
        return []

    # Sort by creation time, newest first
    adapters.sort(key=lambda a: a["created_at"], reverse=True)
    to_remove = adapters[keep_last:]
    removed = []

    for adapter in to_remove:
        path = Path(adapter["path"])
        if path.exists() and "lora_adapter_latest" not in path.name:
            shutil.rmtree(path)
            removed.append(adapter["version"])
            logger.info(f"Removed old adapter: {adapter['version']}")

    return removed


def _record_adapter_in_db(version: str, adapter_path: str) -> None:
    """Record the adapter version in the database."""
    import sqlite3
    db_path = str(settings.data_dir / "psa.db")

    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            """INSERT INTO finetune_runs (adapter_version, num_lessons_used, adapter_path)
               VALUES (?, 0, ?)""",
            (version, adapter_path),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to record adapter in database: {e}")
