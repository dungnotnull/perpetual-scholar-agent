"""perpetual-scholar-agent — CLI entry point.

Usage:
    python -m agent run --once       # Run a single pipeline cycle
    python -m agent start             # Start the scheduler daemon
    python -m agent verify            # Run Phase 0 verification scripts
    python -m agent init              # Initialize database and FAISS index
    python -m agent dashboard         # Start the FastAPI dashboard
"""
from __future__ import annotations

import argparse
import asyncio
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="perpetual-scholar-agent",
        description="Autonomous 24/7 self-evolving research agent",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── run ─────────────────────────────────────────────────────────────────
    run_parser = subparsers.add_parser("run", help="Run pipeline cycles")
    run_parser.add_argument(
        "--mock", action="store_true", default=False,
        help="Run in mock mode (no ML dependencies required)",
    )
    run_parser.add_argument(
        "--once", action="store_true", default=True,
        help="Run one cycle and exit (default)",
    )
    run_parser.add_argument(
        "--source", type=str, default="all",
        choices=["arxiv", "github", "rss", "all"],
        help="Ingestion source to use",
    )
    run_parser.add_argument(
        "--continuous", action="store_true",
        help="Run continuously with the scheduler",
    )

    # ── start ───────────────────────────────────────────────────────────────
    start_parser = subparsers.add_parser("start", help="Start the scheduler daemon")

    # ── verify ──────────────────────────────────────────────────────────────
    verify_parser = subparsers.add_parser("verify", help="Run verification scripts")
    verify_parser.add_argument(
        "--component", type=str, default="all",
        choices=["all", "dependencies", "ollama", "docker", "ingestion", "db"],
        help="Which component to verify",
    )

    # ── init ─────────────────────────────────────────────────────────────────
    init_parser = subparsers.add_parser("init", help="Initialize database and FAISS index")
    init_parser.add_argument(
        "--mock", action="store_true", default=False,
        help="Initialize in mock mode (skip FAISS)",
    )

    # ── dashboard ────────────────────────────────────────────────────────────
    dashboard_parser = subparsers.add_parser("dashboard", help="Start the FastAPI dashboard")
    dashboard_parser.add_argument(
        "--mock", action="store_true", default=False,
        help="Run dashboard in mock mode (use mock data)",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    # Configure structured logging for all commands
    from agent.logging_config import configure_logging
    from agent.config.settings import settings
    configure_logging(settings.log_level)

    import logging
    logger = logging.getLogger(__name__)

    if args.command == "run":
        if args.mock:
            from agent.mock_mode import init_mock_mode
            from agent.mock_pipeline import run_mock_pipeline
            init_mock_mode()
            result = run_mock_pipeline(source=args.source)
        else:
            from agent.orchestrator.pipeline import run_once
            result = asyncio.run(run_once(source=args.source))

        logger.info("run_complete", extra={"result": result})
        print(f"\n{'='*70}")
        print(f"Cycle complete: {result['experiments_run']} experiments, "
              f"{result['lessons_stored']} lessons, "
              f"avg_reward={result['avg_reward']:.3f}")
        print(f"{'='*70}")

    elif args.command == "start":
        from agent.orchestrator.scheduler import start_scheduler
        start_scheduler()

    elif args.command == "verify":
        _run_verify(args.component)

    elif args.command == "init":
        _run_init(args.mock)

    elif args.command == "dashboard":
        from agent.dashboard import run_dashboard
        run_dashboard()


def _run_verify(component: str):
    """Run verification scripts."""
    import subprocess
    from pathlib import Path

    scripts_dir = Path(__file__).parent.parent / "scripts"

    script_map = {
        "dependencies": "verify_dependencies.py",
        "ollama": "verify_ollama.py",
        "docker": "verify_docker.py",
        "ingestion": "verify_ingestion.py",
        "db": "verify_db_vector.py",
    }

    if component == "all":
        scripts = list(script_map.values())
    else:
        scripts = [script_map[component]]

    for script in scripts:
        script_path = scripts_dir / script
        print(f"\n{'='*70}")
        print(f"Running: {script}")
        print(f"{'='*70}")
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(Path(__file__).parent.parent),
        )
        if result.returncode != 0:
            print(f"FAIL: {script} exited with code {result.returncode}")
            sys.exit(result.returncode)

    print(f"\n{'='*70}")
    print("All verifications passed!")
    print(f"{'='*70}")


def _run_init(mock: bool = False):
    """Initialize the database and FAISS index."""
    from agent.database.schema import init_db
    from agent.config.settings import settings
    import logging
    logger = logging.getLogger(__name__)

    print("Initializing perpetual-scholar-agent...")
    if mock:
        print("(Running in MOCK MODE - ML components will be mocked)")
    print()

    print("[1/3] Initializing SQLite database...")
    conn = init_db()
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"  Tables: {tables}")
    conn.close()
    print("  Done.")

    print()
    if mock:
        print("[2/3] Mock FAISS index (skipping real initialization)...")
        from agent.mock_mode import MockFAISSIndex
        idx = MockFAISSIndex()
        print(f"  Dimension: {idx.dimension}")
        print(f"  Vectors: {idx.total_vectors}")
        print("  Done.")
    else:
        print("[2/3] Initializing FAISS index...")
        from agent.vectorstore.faiss_index import init_faiss_index
        idx = init_faiss_index()
        print(f"  Dimension: {idx.dimension}")
        print(f"  Vectors: {idx.total_vectors}")
        print("  Done.")

    print()
    print("[3/3] Creating data directories...")
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.models_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "reports").mkdir(parents=True, exist_ok=True)
    print("  Done.")

    print()
    print("=" * 70)
    print("Initialization complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
