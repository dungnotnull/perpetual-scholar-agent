"""Resilience utilities: retry logic with tenacity and circuit breaker pattern."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

from tenacity import (
    retry,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Retry decorators for common failure patterns
# ---------------------------------------------------------------------------

retry_network = retry(
    stop=stop_after_attempt(3) | stop_after_delay(30),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((
        ConnectionError,
        TimeoutError,
        OSError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)

retry_http = retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type((
        ConnectionError,
        TimeoutError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)

retry_llm = retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=4, max=60),
    retry=retry_if_exception_type((
        ConnectionError,
        TimeoutError,
        RuntimeError,
    )),
    before_sleep=before_sleep_log(logger, logging.WARNING),
    reraise=True,
)


# ---------------------------------------------------------------------------
# Circuit Breaker
# ---------------------------------------------------------------------------

@dataclass
class CircuitBreaker:
    """A simple circuit breaker that prevents operations when failure rate is high.

    Tracks successes and failures over a sliding time window. When the failure
    rate exceeds the threshold, the circuit "opens" and all calls are rejected
    until the cooldown period passes.

    Usage::

        breaker = CircuitBreaker(failure_threshold=0.5, window_seconds=3600)
        if breaker.is_open:
            logger.warning("Circuit breaker open — skipping operation")
            return
        try:
            result = do_risky_thing()
            breaker.record_success()
        except Exception:
            breaker.record_failure()
            raise
    """

    failure_threshold: float = 0.5
    window_seconds: int = 3600
    cooldown_seconds: int = 300
    _successes: list = field(default_factory=list)
    _failures: list = field(default_factory=list)
    _opened_at: Optional[float] = None

    def _prune(self) -> None:
        """Remove events outside the time window."""
        cutoff = time.time() - self.window_seconds
        self._successes = [t for t in self._successes if t > cutoff]
        self._failures = [t for t in self._failures if t > cutoff]

    @property
    def is_open(self) -> bool:
        """Check if the circuit breaker is open (blocking calls)."""
        if self._opened_at is not None:
            if time.time() - self._opened_at > self.cooldown_seconds:
                self._opened_at = None
                return False
            return True

        self._prune()
        total = len(self._successes) + len(self._failures)
        if total < 2:
            return False

        failure_rate = len(self._failures) / total
        if failure_rate >= self.failure_threshold:
            self._opened_at = time.time()
            logger.warning(
                f"Circuit breaker OPENED: failure rate {failure_rate:.1%} "
                f"exceeds threshold {self.failure_threshold:.1%}"
            )
            return True
        return False

    def record_success(self) -> None:
        """Record a successful operation."""
        self._successes.append(time.time())

    def record_failure(self) -> None:
        """Record a failed operation."""
        self._failures.append(time.time())

    @property
    def stats(self) -> dict:
        """Return current circuit breaker statistics."""
        self._prune()
        total = len(self._successes) + len(self._failures)
        return {
            "successes": len(self._successes),
            "failures": len(self._failures),
            "total": total,
            "failure_rate": len(self._failures) / total if total > 0 else 0.0,
            "is_open": self.is_open,
        }


# Global circuit breaker for sandbox experiments
sandbox_circuit_breaker = CircuitBreaker(
    failure_threshold=0.5,
    window_seconds=3600,
    cooldown_seconds=300,
)
