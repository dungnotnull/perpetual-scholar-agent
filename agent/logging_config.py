"""Central logging configuration — structured JSON logging via structlog."""
from __future__ import annotations

import logging
import sys
from typing import Optional

import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured JSON logging for the entire agent.

    Call this once at application startup. All modules using
    ``logging.getLogger(__name__)`` will automatically produce
    structured JSON output.

    Args:
        log_level: Logging level string (DEBUG, INFO, WARNING, ERROR).
    """
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Also configure standard logging to use structlog
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            processor=structlog.processors.JSONRenderer(),
            foreign_pre_chain=[
                structlog.stdlib.add_log_level,
                structlog.stdlib.add_logger_name,
                structlog.processors.TimeStamper(fmt="iso"),
            ],
        )
    )
    root_logger.handlers = [handler]

    # Quieten noisy third-party loggers
    for noisy in [
        "urllib3", "httpx", "docker", "urllib3.connectionpool",
        "sentence_transformers", "transformers", "PIL", "matplotlib",
    ]:
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger for a module.

    Usage::

        from agent.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("event_occurred", key="value")
    """
    return structlog.get_logger(name)
