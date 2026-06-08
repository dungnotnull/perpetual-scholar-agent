"""Sandbox execution: resource limit enforcement."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ResourceLimits:
    """Container resource limits."""
    cpu_count: int = 2
    memory_mb: int = 2048
    timeout_seconds: int = 60
    network_disabled: bool = True
    pids_limit: int = 100
    read_only_root: bool = False

    @classmethod
    def from_settings(cls) -> "ResourceLimits":
        """Create limits from application settings."""
        # Parse memory limit string (e.g., "2g" → 2048 MB)
        mem_str = settings.sandbox_memory_limit.lower().strip()
        if mem_str.endswith("g"):
            memory_mb = int(float(mem_str[:-1]) * 1024)
        elif mem_str.endswith("m"):
            memory_mb = int(mem_str[:-1])
        else:
            memory_mb = 2048

        return cls(
            cpu_count=settings.sandbox_cpu_limit,
            memory_mb=memory_mb,
            timeout_seconds=settings.sandbox_timeout_seconds,
            network_disabled=settings.sandbox_network_disabled,
        )

    def to_docker_kwargs(self) -> dict:
        """Convert to Docker SDK container.create() keyword arguments."""
        return {
            "nano_cpus": self.cpu_count * 1_000_000_000,
            "mem_limit": f"{self.memory_mb}m",
            "memswap_limit": f"{self.memory_mb}m",  # No swap
            "network_disabled": self.network_disabled,
            "pids_limit": self.pids_limit,
        }


def validate_benchmark_result(
    exit_code: int,
    stdout: str,
    stderr: str,
    timed_out: bool,
) -> tuple[bool, str]:
    """Validate that a sandbox execution produced usable results.

    Args:
        exit_code: Container exit code.
        stdout: Container stdout.
        stderr: Container stderr.
        timed_out: Whether the container was killed for timeout.

    Returns:
        Tuple of (is_valid: bool, reason: str).
    """
    if timed_out:
        return False, f"Container timed out (exit_code={exit_code})"

    if exit_code != 0:
        return False, f"Container exited with code {exit_code}: {stderr[:500]}"

    if not stdout:
        return False, "Container produced no output"

    return True, "OK"


# Pre-computed default limits
DEFAULT_LIMITS = ResourceLimits.from_settings()
