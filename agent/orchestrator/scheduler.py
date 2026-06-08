"""Orchestrator: APScheduler-based daemon for continuous operation with graceful shutdown."""
from __future__ import annotations

import asyncio
import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from agent.config.settings import settings
from agent.logging_config import configure_logging

logger = logging.getLogger(__name__)

scheduler = BlockingScheduler()


def _ingestion_job():
    """Daily ingestion pipeline job."""
    configure_logging(settings.log_level)
    logger.info("scheduled_ingestion_job_started")
    try:
        result = asyncio.run(run_once(source="all"))
        logger.info("scheduled_ingestion_job_complete", extra={"result": result})
    except Exception as e:
        logger.error("scheduled_ingestion_job_failed", extra={"error": str(e)})


def _finetune_check_job():
    """Weekly fine-tuning check job."""
    configure_logging(settings.log_level)
    logger.info("scheduled_finetune_check_started")
    try:
        triggered = asyncio.run(trigger_finetune_if_needed())
        logger.info("scheduled_finetune_check_complete", extra={"triggered": triggered})
    except Exception as e:
        logger.error("scheduled_finetune_check_failed", extra={"error": str(e)})


def _brain_update_job():
    """Weekly SECOND-KNOWLEDGE-BRAIN.md update job."""
    configure_logging(settings.log_level)
    logger.info("scheduled_brain_update_started")
    try:
        asyncio.run(update_knowledge_brain())
        logger.info("scheduled_brain_update_complete")
    except Exception as e:
        logger.error("scheduled_brain_update_failed", extra={"error": str(e)})


def _report_job():
    """Weekly digest report job."""
    configure_logging(settings.log_level)
    logger.info("scheduled_report_job_started")
    try:
        asyncio.run(save_weekly_digest())
        logger.info("scheduled_report_job_complete")
    except Exception as e:
        logger.error("scheduled_report_job_failed", extra={"error": str(e)})


def start_scheduler():
    """Start the APScheduler daemon with all cron jobs and graceful shutdown."""
    configure_logging(settings.log_level)

    # Import here to avoid circular imports at module level
    from agent.orchestrator.pipeline import run_once
    from agent.finetune.trigger import trigger_finetune_if_needed
    from agent.reporting.brain_updater import update_knowledge_brain
    from agent.monitoring.reporter import save_weekly_digest
    from agent.database.schema import init_db

    # Initialize database on startup
    conn = init_db()
    conn.close()
    logger.info("database_initialized")

    # Parse cron expressions
    ing_parts = settings.schedule_ingestion_cron.split()
    ft_parts = settings.schedule_finetune_cron.split()
    bu_parts = settings.schedule_brain_update_cron.split()
    rp_parts = settings.schedule_report_cron.split()

    # Register ingestion job (default: daily at 02:00 UTC)
    scheduler.add_job(
        _ingestion_job,
        CronTrigger(
            minute=ing_parts[0],
            hour=ing_parts[1] if len(ing_parts) > 1 else "2",
        ),
        id="ingestion",
        name="Daily ingestion pipeline",
        max_instances=1,
        misfire_grace_time=300,
    )

    # Register fine-tune check (default: weekly Sunday 03:00 UTC)
    scheduler.add_job(
        _finetune_check_job,
        CronTrigger(
            minute=ft_parts[0],
            hour=ft_parts[1] if len(ft_parts) > 1 else "3",
            day_of_week=ft_parts[4] if len(ft_parts) > 4 else "sun",
        ),
        id="finetune_check",
        name="Weekly fine-tune check",
        max_instances=1,
        misfire_grace_time=600,
    )

    # Register brain update (default: weekly Sunday 06:00 UTC)
    scheduler.add_job(
        _brain_update_job,
        CronTrigger(
            minute=bu_parts[0],
            hour=bu_parts[1] if len(bu_parts) > 1 else "6",
            day_of_week=bu_parts[4] if len(bu_parts) > 4 else "sun",
        ),
        id="brain_update",
        name="Weekly knowledge brain update",
        max_instances=1,
        misfire_grace_time=600,
    )

    # Register weekly report (default: weekly Monday 08:00 UTC)
    scheduler.add_job(
        _report_job,
        CronTrigger(
            minute=rp_parts[0],
            hour=rp_parts[1] if len(rp_parts) > 1 else "8",
            day_of_week=rp_parts[4] if len(rp_parts) > 4 else "mon",
        ),
        id="weekly_report",
        name="Weekly digest report",
        max_instances=1,
        misfire_grace_time=600,
    )

    # Graceful shutdown handler
    def shutdown_handler(signum, frame):
        logger.info("shutdown_signal_received", extra={"signal": signum})
        scheduler.shutdown(wait=False)

        # Clean up Docker containers
        try:
            from agent.sandbox.executor import SandboxExecutor
            executor = SandboxExecutor()
            count = executor.cleanup_all()
            logger.info("docker_containers_cleaned", extra={"count": count})
        except Exception as e:
            logger.warning("docker_cleanup_failed", extra={"error": str(e)})

        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    logger.info(
        "scheduler_starting",
        extra={
            "ingestion": settings.schedule_ingestion_cron,
            "finetune": settings.schedule_finetune_cron,
            "brain_update": settings.schedule_brain_update_cron,
            "report": settings.schedule_report_cron,
        },
    )

    scheduler.start()
