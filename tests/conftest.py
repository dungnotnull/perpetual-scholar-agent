"""
Pytest configuration and shared fixtures.

This file provides pytest hooks and common fixtures used across all tests.
"""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any, Generator
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.fixtures.mocks import (
    MockOllamaBackend,
    MockClaudeBackend,
    MockDockerClient,
    MockDatabase,
    MockRedis,
    MockEmbeddingModel,
    create_mock_ollama,
    create_mock_claude,
    create_mock_docker,
    create_mock_database,
    create_mock_redis,
    create_mock_embedding_model
)


# Pytest configuration markers

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests (real dependencies)")
    config.addinivalue_line("markers", "slow: Slow-running tests (> 1 second)")
    config.addinivalue_line("markers", "benchmark: Performance benchmarks")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")


# Global fixtures

@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """Provide project root path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_path(project_root_path: Path) -> Path:
    """Provide test data directory path."""
    test_data = project_root_path / "tests" / "fixtures"
    test_data.mkdir(parents=True, exist_ok=True)
    return test_data


@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """Provide temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


# Mock fixtures

@pytest.fixture(scope="function")
def mock_ollama() -> MockOllamaBackend:
    """Provide mock Ollama backend."""
    backend = create_mock_ollama()
    yield backend
    backend.reset()


@pytest.fixture(scope="function")
def mock_claude() -> MockClaudeBackend:
    """Provide mock Claude backend."""
    backend = create_mock_claude()
    yield backend
    backend.reset()


@pytest.fixture(scope="function")
def mock_docker() -> MockDockerClient:
    """Provide mock Docker client."""
    client = create_mock_docker()
    yield client
    client.reset()


@pytest.fixture(scope="function")
def mock_db() -> MockDatabase:
    """Provide mock database."""
    db = create_mock_database()
    yield db
    db.reset()


@pytest.fixture(scope="function")
def mock_redis() -> MockRedis:
    """Provide mock Redis client."""
    redis = create_mock_redis()
    yield redis
    redis.flushdb()


@pytest.fixture(scope="function")
def mock_embedding() -> MockEmbeddingModel:
    """Provide mock embedding model."""
    model = create_mock_embedding_model()
    yield model
    model.reset()


# Data fixtures

@pytest.fixture(scope="function")
def sample_paper() -> Dict[str, Any]:
    """Provide sample paper data."""
    return {
        "id": "arxiv:2301.00001",
        "title": "Optimizing Database Query Performance with Machine Learning",
        "authors": ["Jane Doe", "John Smith"],
        "abstract": "This paper presents a novel approach to optimizing database queries using machine learning techniques. We demonstrate a 35% improvement in query latency on standard benchmarks.",
        "published": "2025-01-15",
        "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf",
        "source": "arxiv",
        "category": "cs.DB",
        "relevance_score": 0.85
    }


@pytest.fixture(scope="function")
def sample_papers() -> Dict[str, Any]:
    """Provide multiple sample papers."""
    return [
        {
            "id": "arxiv:2301.00001",
            "title": "Optimizing Database Query Performance",
            "authors": ["Jane Doe"],
            "abstract": "Database optimization techniques using ML",
            "published": "2025-01-15",
            "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf",
            "source": "arxiv"
        },
        {
            "id": "arxiv:2301.00002",
            "title": "Advanced Caching Strategies for Web Applications",
            "authors": ["John Smith", "Bob Johnson"],
            "abstract": "Novel caching approaches for high-traffic web services",
            "published": "2025-01-16",
            "pdf_url": "https://arxiv.org/pdf/2301.00002.pdf",
            "source": "arxiv"
        },
        {
            "id": "github:trending/repo-1",
            "title": "Fast Async I/O Patterns in Python",
            "authors": ["dev_user"],
            "abstract": "Repository showcasing high-performance async patterns",
            "published": "2025-01-17",
            "url": "https://github.com/user/repo-1",
            "source": "github",
            "stars": 1500
        }
    ]


@pytest.fixture(scope="function")
def sample_lesson() -> Dict[str, Any]:
    """Provide sample lesson data."""
    return {
        "id": "lesson-001",
        "title": "Use prepared statements for database queries",
        "source": "arxiv:2301.00001",
        "domain": "backend_performance",
        "improvement_metric": "query_latency",
        "improvement_value": 0.35,
        "baseline_value": 100.0,
        "code_example": """
def execute_query(conn, query, params):
    cursor = conn.cursor()
    cursor.execute(query, params)
    return cursor.fetchall()
""",
        "description": "Prepared statements reduce parsing overhead and prevent SQL injection",
        "verified_at": "2025-01-15T10:30:00Z",
        "confidence": 0.92
    }


@pytest.fixture(scope="function")
def sample_experiment_result() -> Dict[str, Any]:
    """Provide sample experiment result."""
    return {
        "id": "exp-001",
        "paper_id": "arxiv:2301.00001",
        "code": """
def optimized_query():
    # Optimized implementation
    pass
""",
        "exit_code": 0,
        "stdout": "Test passed: 1000 operations in 1.2s",
        "stderr": "",
        "execution_time": 1.2,
        "memory_usage_mb": 128,
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture(scope="function")
def sample_benchmark_result() -> Dict[str, Any]:
    """Provide sample benchmark result."""
    return {
        "experiment_id": "exp-001",
        "metric_name": "throughput",
        "baseline_value": 100.0,
        "experiment_value": 135.0,
        "improvement_percent": 35.0,
        "statistical_significance": 0.95,
        "sample_size": 1000,
        "timestamp": datetime.utcnow().isoformat()
    }


@pytest.fixture(scope="function")
def sample_code_snippet() -> str:
    """Provide sample Python code snippet."""
    return """
import asyncio
from typing import List

async def fetch_data(items: List[str]) -> dict:
    '''Fetch data asynchronously'''
    tasks = [asyncio.create_task(fetch_item(item)) for item in items]
    results = await asyncio.gather(*tasks)
    return dict(zip(items, results))

async def fetch_item(item: str) -> str:
    '''Fetch single item'''
    await asyncio.sleep(0.1)
    return f"result-{item}"
"""


@pytest.fixture(scope="function")
def sample_env_vars() -> Dict[str, str]:
    """Provide sample environment variables."""
    return {
        "ENVIRONMENT": "test",
        "LOG_LEVEL": "DEBUG",
        "DOMAIN_FOCUS": "backend_performance",
        "LLM_PROVIDER": "ollama",
        "OLLAMA_BASE_URL": "http://localhost:11434",
        "OLLAMA_MODEL": "qwen2.5-coder:7b",
        "DATABASE_URL": "sqlite:///test.db",
        "REDIS_URL": "redis://localhost:6379",
        "SANDBOX_CPU_LIMIT": "2",
        "SANDBOX_MEMORY_LIMIT": "2g",
        "EXPERIMENT_TIMEOUT_SECONDS": "60"
    }


# Test configuration fixtures

@pytest.fixture(scope="function")
def test_settings(monkeypatch, sample_env_vars):
    """Provide test configuration settings."""
    for key, value in sample_env_vars.items():
        monkeypatch.setenv(key, value)

    from agent.config.settings import Settings
    try:
        return Settings.load()
    except Exception:
        # Return basic mock settings if loading fails
        class MockSettings:
            environment = "test"
            log_level = "DEBUG"
            domain_focus = "backend_performance"
            llm_provider = "ollama"
            ollama_base_url = "http://localhost:11434"
            ollama_model = "qwen2.5-coder:7b"
            database_url = "sqlite:///test.db"
            redis_url = "redis://localhost:6379"
            sandbox_cpu_limit = 2
            sandbox_memory_limit = "2g"
            experiment_timeout_seconds = 60

        return MockSettings()


# Performance testing fixtures

@pytest.fixture(scope="function")
def performance_thresholds() -> Dict[str, float]:
    """Provide performance threshold values."""
    return {
        "max_experiment_time": 300.0,  # 5 minutes
        "max_embedding_time": 5.0,  # 5 seconds
        "max_deduplication_time": 10.0,  # 10 seconds
        "max_code_generation_time": 30.0,  # 30 seconds
        "max_sandbox_startup_time": 10.0,  # 10 seconds
        "min_throughput": 10.0,  # experiments per hour
    }


@pytest.fixture(scope="function")
def sample_large_dataset(size: int = 10000) -> list:
    """Generate large dataset for performance testing."""
    return [
        {
            "id": f"item-{i}",
            "title": f"Test Item {i}",
            "content": f"Content for item {i}" * 10,
            "timestamp": datetime.utcnow().isoformat()
        }
        for i in range(size)
    ]


# Helper fixtures

@pytest.fixture(scope="function")
def assert_no_exceptions(caplog):
    """Helper to assert no exceptions were logged."""
    def _assert():
        assert not any(
            record.levelname == "ERROR" or
            "exception" in record.message.lower() or
            "error" in record.message.lower()
            for record in caplog.records
        ), "Errors or exceptions were logged"
    return _assert


@pytest.fixture(scope="function")
def freeze_time(monkeypatch):
    """Helper to freeze time for deterministic testing."""
    frozen_time = datetime(2025, 1, 15, 10, 30, 0)

    class FrozenDatetime:
        @classmethod
        def utcnow(cls):
            return frozen_time

        @classmethod
        def advance(cls, seconds=0, minutes=0, hours=0):
            nonlocal frozen_time
            from datetime import timedelta
            frozen_time += timedelta(seconds=seconds, minutes=minutes, hours=hours)

    monkeypatch.setattr("datetime.datetime", FrozenDatetime)
    return FrozenDatetime


# CLI testing fixtures

@pytest.fixture(scope="function")
def mock_cli_args(monkeypatch):
    """Helper to mock CLI arguments."""
    def _mock_args(args: list):
        monkeypatch.setattr("sys.argv", ["psa-agent"] + args)
    return _mock_args


@pytest.fixture(scope="function")
def capture_output(monkeypatch, capsys):
    """Helper to capture CLI output."""
    import io
    from contextlib import redirect_stdout, redirect_stderr

    class OutputCapture:
        def __enter__(self):
            self.stdout_buf = io.StringIO()
            self.stderr_buf = io.StringIO()
            return self

        def __exit__(self, *args):
            pass

        @property
        def stdout(self):
            return self.stdout_buf.getvalue()

        @property
        def stderr(self):
            return self.stderr_buf.getvalue()

    return OutputCapture


# Async testing fixtures

@pytest.fixture(scope="function")
def event_loop():
    """Create event loop for async tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Cleanup fixtures

@pytest.fixture(scope="function", autouse=True)
def cleanup_test_resources(request):
    """Automatically clean up test resources."""
    yield
    # Cleanup code runs after each test
    test_name = request.node.name

    # Clean up any temporary files
    temp_files = Path(__file__).parent / "temp"
    if temp_files.exists():
        for f in temp_files.glob("test_*"):
            f.unlink(missing_ok=True)

    # Clean up test databases
    test_dbs = Path(__file__).parent.glob("*.db")
    for db in test_dbs:
        db.unlink(missing_ok=True)


# Skip decorators

def skip_if_no_docker(func):
    """Skip test if Docker is not available."""
    import shutil
    return pytest.mark.skipif(
        not shutil.which("docker"),
        reason="Docker not available"
    )(func)


def skip_if_no_ollama(func):
    """Skip test if Ollama is not available."""
    import requests
    def check_ollama():
        try:
            return requests.get("http://localhost:11434/api/tags").status_code == 200
        except:
            return False
    return pytest.mark.skipif(
        not check_ollama(),
        reason="Ollama not available"
    )(func)


def skip_if_slow_test(func):
    """Skip test unless running slow tests."""
    return pytest.mark.skipif(
        "not config.getoption('--runslow', default=False)",
        reason="Slow test skipped (use --runslow)"
    )(func)
