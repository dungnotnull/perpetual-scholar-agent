# Testing Guide

This guide covers testing conventions, strategies, and best practices for the Perpetual Scholar Agent.

## Table of Contents

- [Testing Philosophy](#testing-philosophy)
- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)
- [Mocking and Fixtures](#mocking-and-fixtures)
- [Integration Testing](#integration-testing)
- [Performance Testing](#performance-testing)
- [Continuous Integration](#continuous-integration)

## Testing Philosophy

We follow test-driven development (TDD) principles with emphasis on:

1. **Fast Feedback**: Unit tests run in seconds, integration tests in minutes
2. **Isolation**: Each test is independent and can run alone
3. **Clarity**: Tests serve as documentation for expected behavior
4. **Realism**: Integration tests use real infrastructure when possible

### Testing Pyramid

```
           E2E (5%)
          /        \
     Integration (15%)
    /                \
   Unit Tests (80%)
```

- **Unit Tests**: Test individual functions and classes in isolation
- **Integration Tests**: Test module interactions with real dependencies
- **E2E Tests**: Test complete workflows (minimal, slow)

## Test Organization

```
tests/
├── unit/                    # Fast, isolated unit tests
│   ├── test_config.py       # Configuration module tests
│   ├── test_ingestion.py    # Data ingestion tests
│   ├── test_reward.py       # Reward calculation tests
│   ├── test_llm.py          # LLM backend tests
│   └── test_sandbox.py      # Sandbox execution tests
├── integration/             # Module interaction tests
│   ├── test_pipeline.py     # Full ingestion pipeline
│   ├── test_training.py     # RL training loop
│   └── test_finetuning.py   # LoRA fine-tuning
├── e2e/                     # End-to-end workflow tests
│   ├── test_daily_cycle.py  # Daily research cycle
│   └── test_recovery.py     # Backup/recovery workflows
├── fixtures/                # Test fixtures and factories
│   ├── mock_papers.json
│   └── sample_code.py
└── conftest.py              # Shared pytest configuration
```

### Naming Conventions

- **File names**: `test_<module>.py`
- **Test classes**: `Test<ClassName>`
- **Test functions**: `test_<scenario>_<expected outcome>`
- **Fixtures**: `<resource>_fixture`

## Running Tests

### All Tests

```bash
# Run entire suite
pytest

# With coverage
pytest --cov=agent --cov-report=html --cov-report=term
```

### Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific module
pytest tests/unit/test_config.py

# Specific test
pytest tests/unit/test_config.py::test_load_settings
```

### Filtering

```bash
# Run only fast tests
pytest -m "not slow"

# Run only smoke tests
pytest -m smoke

# Run only tests matching pattern
pytest -k "test_load_"
```

### Parallel Execution

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Distribute by test file
pytest -n 4 --dist loadfile
```

### Debugging

```bash
# Stop on first failure
pytest -x

# Drop into debugger on failure
pytest --pdb

# Show local variables on failure
pytest -l

# Print output of passing tests
pytest -s
```

## Writing Tests

### Basic Unit Test

```python
import pytest
from agent.ingestion.deduplicator import Deduplicator

class TestDeduplicator:
    @pytest.fixture
    def deduplicator(self):
        return Deduplicator()
    
    @pytest.fixture
    def sample_items(self):
        return [
            {"id": "1", "title": "Paper A", "content": "..."},
            {"id": "2", "title": "Paper A", "content": "..."},  # Duplicate
            {"id": "3", "title": "Paper B", "content": "..."},
        ]
    
    def test_removes_duplicates_by_title(self, deduplicator, sample_items):
        unique_items = deduplicator.deduplicate(sample_items)
        assert len(unique_items) == 2
        assert all(item["title"] != "Paper A" for item in unique_items[1:])
```

### Test with Mocks

```python
from unittest.mock import Mock, patch
from agent.llm.ollama_backend import OllamaBackend

class TestOllamaBackend:
    @patch('requests.post')
    def test_generate_code_success(self, mock_post):
        mock_post.return_value.json.return_value = {
            "response": "def hello(): pass",
            "model": "qwen2.5-coder:7b"
        }
        
        backend = OllamaBackend(base_url="http://localhost:11434")
        result = backend.generate("Write hello world")
        
        assert "def hello" in result
        mock_post.assert_called_once()
```

### Parameterized Tests

```python
@pytest.mark.parametrize("input,expected", [
    ("backend performance", "backend_performance"),
    ("AI/ML  ", "ai_ml"),
    ("C++ optimization", "cpp_optimization"),
])
def test_sanitize_domain(input, expected):
    from agent.config.utils import sanitize_domain
    assert sanitize_domain(input) == expected
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_paper_fetch():
    from agent.ingestion.arxiv_fetcher import ArxivFetcher
    fetcher = ArxivFetcher()
    papers = await fetcher.fetch_papers(max_results=5)
    assert len(papers) <= 5
```

### Exception Testing

```python
def test_invalid_config_raises_error():
    with pytest.raises(ValueError, match="DOMAIN_FOCUS is required"):
        Settings.load(env_file="invalid.env")
```

## Test Coverage

### Coverage Goals

- **Overall**: ≥ 80% code coverage
- **Critical paths**: 100% coverage (reward calculation, sandbox execution)
- **Documentation**: ≥ 70% coverage

### Generating Reports

```bash
# HTML report
pytest --cov=agent --cov-report=html
open htmlcov/index.html

# Terminal report
pytest --cov=agent --cov-report=term-missing

# JSON report (for CI)
pytest --cov=agent --cov-report=json
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = agent
omit = 
    */tests/*
    */migrations/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    if DEBUG:
    raise NotImplementedError
    if __name__ == .__main__.:
```

## Mocking and Fixtures

### Mock Infrastructure

Located in `tests/fixtures/mocks.py`:

```python
from unittest.mock import Mock, MagicMock
from typing import Optional

class MockOllamaBackend:
    """Mock Ollama backend for testing"""
    
    def __init__(self, responses: Optional[dict] = None):
        self.responses = responses or {
            "generate": "def example(): pass",
            "chat": "I can help with that"
        }
        self.call_count = 0
    
    def generate(self, prompt: str) -> str:
        self.call_count += 1
        return self.responses.get("generate", "")
    
    def chat(self, messages: list) -> str:
        self.call_count += 1
        return self.responses.get("chat", "")

class MockClaudeBackend:
    """Mock Claude API backend for testing"""
    
    def __init__(self, api_key: str = "test-key"):
        self.api_key = api_key
        self.messages = []
    
    def message(self, content: str) -> str:
        self.messages.append(content)
        return "Mock Claude response"

class MockDockerClient:
    """Mock Docker client for sandbox testing"""
    
    def __init__(self):
        self.containers = []
        self.images = []
    
    def containers.create(self, **kwargs):
        mock_container = Mock()
        mock_container.id = f"mock-{len(self.containers)}"
        mock_container.status = "running"
        self.containers.append(mock_container)
        return mock_container
    
    def containers.get(self, container_id):
        return next((c for c in self.containers if c.id == container_id), None)
```

### Pytest Fixtures

In `tests/conftest.py`:

```python
import pytest
from agent.config.settings import Settings
from tests.fixtures.mocks import MockOllamaBackend, MockDockerClient

@pytest.fixture
def test_settings():
    """Provide test settings"""
    return Settings.load(env_file=".env.test")

@pytest.fixture
def mock_ollama():
    """Mock Ollama backend"""
    return MockOllamaBackend()

@pytest.fixture
def mock_docker():
    """Mock Docker client"""
    return MockDockerClient()

@pytest.fixture
def sample_paper():
    """Sample paper fixture"""
    return {
        "id": "arxiv:2301.00001",
        "title": "Test Paper",
        "authors": ["Author One", "Author Two"],
        "abstract": "This is a test abstract",
        "published": "2025-01-01",
        "pdf_url": "https://arxiv.org/pdf/2301.00001.pdf"
    }

@pytest.fixture
def sample_lesson():
    """Sample lesson fixture"""
    return {
        "id": "lesson-001",
        "title": "Optimize Database Queries",
        "source": "arxiv:2301.00001",
        "improvement_metric": "query_latency",
        "improvement_value": 0.35,
        "code_example": "SELECT * FROM table WHERE indexed = ?",
        "verified_at": "2025-01-01T12:00:00Z"
    }
```

## Integration Testing

### Database Integration

```python
@pytest.mark.integration
def test_database_lesson_storage(test_settings):
    """Test lesson storage in real database"""
    from agent.database.schema import LessonStore
    
    store = LessonStore(test_settings.database_url)
    lesson = sample_lesson()
    
    # Store and retrieve
    store.store_lesson(lesson)
    retrieved = store.get_lesson(lesson["id"])
    
    assert retrieved["id"] == lesson["id"]
    assert retrieved["title"] == lesson["title"]
```

### Sandbox Integration

```python
@pytest.mark.integration
@pytest.mark.slow
def test_sandbox_code_execution(test_settings):
    """Test actual Docker sandbox execution"""
    from agent.sandbox.executor import SandboxExecutor
    
    executor = SandboxExecutor(test_settings)
    code = """
def add(a, b):
    return a + b

result = add(2, 3)
print(f"Result: {result}")
"""
    
    result = executor.execute(code)
    assert result.exit_code == 0
    assert "Result: 5" in result.output
```

### LLM Integration

```python
@pytest.mark.integration
@pytest.mark.slow
def test_ollama_code_generation(test_settings):
    """Test real Ollama code generation"""
    from agent.llm.ollama_backend import OllamaBackend
    
    backend = OllamaBackend(test_settings.ollama_base_url)
    prompt = "Write a Python function to reverse a string"
    
    code = backend.generate(prompt)
    
    assert "def" in code
    assert "return" in code
```

## Performance Testing

### Benchmarking

```python
@pytest.mark.benchmark
def test_deduplication_performance(benchmark):
    """Benchmark deduplication on large dataset"""
    from agent.ingestion.deduplicator import Deduplicator
    
    deduplicator = Deduplicator()
    large_dataset = generate_test_items(10000)
    
    result = benchmark(deduplicator.deduplicate, large_dataset)
    assert len(result) < len(large_dataset)
```

### Load Testing

```python
@pytest.mark.slow
@pytest.mark.load
def test_concurrent_experiments():
    """Test system under concurrent experiment load"""
    from agent.execution.scheduler import ExperimentScheduler
    
    scheduler = ExperimentScheduler(max_concurrent=10)
    experiments = [create_mock_experiment() for _ in range(20)]
    
    results = scheduler.run_all(experiments)
    
    assert all(r.status != "failed" for r in results)
    assert scheduler.execution_time < 60  # seconds
```

### Resource Monitoring

```python
@pytest.mark.monitoring
def test_memory_leak():
    """Test for memory leaks during long-running operation"""
    import tracemalloc
    
    tracemalloc.start()
    snapshot1 = tracemalloc.take_snapshot()
    
    # Run operation 100 times
    for _ in range(100):
        process_paper_batch(large_batch)
    
    snapshot2 = tracemalloc.take_snapshot()
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    
    # Top memory increase should be reasonable
    assert top_stats[0].size_diff < 10_000_000  # 10MB
```

## Test Markers

Use pytest markers to categorize tests:

```python
# pytest.ini
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (real dependencies)",
    "slow: Slow-running tests (> 1 second)",
    "benchmark: Performance benchmarks",
    "smoke: Quick smoke tests",
]
```

Usage:

```python
@pytest.mark.unit
def test_fast_calculation():
    assert 1 + 1 == 2

@pytest.mark.integration
@pytest.mark.slow
def test_database_query():
    # Slow database test
    pass

@pytest.mark.smoke
def test_basic_functionality():
    # Critical path smoke test
    pass
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt
      
      - name: Run unit tests
        run: pytest tests/unit/ --cov=agent --cov-report=xml
      
      - name: Run integration tests
        run: pytest tests/integration/
        env:
          DATABASE_URL: postgresql://test:test@localhost/test
          REDIS_URL: redis://localhost
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-unit
        name: Run unit tests
        entry: pytest tests/unit/
        language: system
        pass_filenames: false
      
      - id: pytest-quick
        name: Run quick tests
        entry: pytest -m "not slow"
        language: system
        pass_filenames: false
```

## Best Practices

### DO's

1. **Test behavior, not implementation**
   ```python
   # Good
   def test_returns_sorted_list():
       result = sort_items(items)
       assert result == sorted(items)
   
   # Bad
   def test_uses_bubble_sort():
       with patch('agent.sort.bubble_sort') as mock_sort:
           sort_items(items)
           mock_sort.assert_called_once()
   ```

2. **Use descriptive test names**
   ```python
   # Good
   def test_removes_duplicate_papers_by_arxiv_id():
       pass
   
   # Bad
   def test_dedup():
       pass
   ```

3. **Follow AAA pattern (Arrange-Act-Assert)**
   ```python
   def test_paper_scoring():
       # Arrange
       paper = create_test_paper(title="...", abstract="...")
       
       # Act
       score = calculate_relevance(paper)
       
       # Assert
       assert 0 <= score <= 1
   ```

4. **Test edge cases**
   ```python
   @pytest.mark.parametrize("input", [
       "",  # Empty
       " ",  # Whitespace
       "a"*10000,  # Very long
       None,  # None
   ])
   def test_handles_edge_cases(input):
       result = process_input(input)
       assert result is not None
   ```

### DON'Ts

1. **Don't test everything**
   - Public APIs: Yes
   - Internal helpers: Only if complex
   - Trivial getters/setters: No

2. **Don't make tests dependent on each other**
   ```python
   # Bad
   def test_step_1():
       global state
       state = "modified"
   
   def test_step_2():
       assert state == "modified"  # Depends on test_step_1
   ```

3. **Don't use random data without seeding**
   ```python
   # Bad
   def test_random_data():
       data = generate_random_data()  # Non-reproducible
   
   # Good
   def test_random_data_seeded():
       random.seed(42)
       data = generate_random_data()  # Reproducible
   ```

4. **Don't ignore flaky tests**
   - Fix time-dependent tests with mocking
   - Use `pytest retries` for truly intermittent network issues
   - Never mark as `xfail` without filing a bug

## Testing Checklist

Before submitting PR:

- [ ] All tests pass locally (`pytest`)
- [ ] New tests added for new functionality
- [ ] Coverage maintained or improved
- [ ] No `pytest.warns` warnings
- [ ] Integration tests pass (if applicable)
- [ ] No hardcoded test data (use fixtures)
- [ ] Tests follow naming conventions
- [ ] No commented-out test code

## Resources

- **Pytest Documentation**: https://docs.pytest.org
- **Python Testing**: https://docs.python.org/3/library/unittest.html
- **Test Coverage**: https://coverage.readthedocs.io
- **Mocking**: https://docs.python.org/3/library/unittest.mock.html
- **Property-Based Testing**: https://hypothesis.readthedocs.io
