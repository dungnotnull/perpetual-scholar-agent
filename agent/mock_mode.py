"""Mock mode for running perpetual-scholar-agent without heavy ML dependencies.

This mode allows the agent to run and demonstrate functionality without requiring:
- FAISS (vector search)
- Ollama (LLM backend)
- Docker (sandbox execution)
- Stable-Baselines3 (RL training)
- Sentence Transformers (embeddings)

Use: python -m agent run --mock
"""

import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import random
import time

logger = logging.getLogger(__name__)


@dataclass
class MockResult:
    """Mock result from pipeline operations."""
    success: bool = True
    data: Dict[str, Any] = None
    message: str = "Mock operation completed"

    def __post_init__(self):
        if self.data is None:
            self.data = {}


class MockFAISSIndex:
    """Mock FAISS index for vector search."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors = []

    def add(self, vector: List[float], metadata: Dict = None) -> str:
        """Add a vector to the mock index."""
        self.vectors.append({"vector": vector, "metadata": metadata or {}})
        return f"mock_id_{len(self.vectors)}"

    def search(self, query_vector: List[float], k: int = 5) -> List[Dict]:
        """Return mock search results."""
        results = []
        for i, item in enumerate(self.vectors[:k]):
            results.append({
                "id": f"mock_id_{i}",
                "score": random.random(),
                "metadata": item.get("metadata", {})
            })
        return results

    @property
    def total_vectors(self) -> int:
        return len(self.vectors)


class MockLLMBackend:
    """Mock LLM backend for generating text."""

    def __init__(self):
        self.call_count = 0

    def generate(self, prompt: str, system: str = "") -> str:
        """Return mock response based on prompt context."""
        self.call_count += 1

        if "summarize" in prompt.lower() or "extract" in prompt.lower():
            return self._mock_summary()
        elif "generate code" in prompt.lower():
            return self._mock_code()
        else:
            return "Mock LLM response"

    def _mock_summary(self) -> str:
        """Return mock paper summary."""
        import json
        return json.dumps({
            "technique_name": "Mock Optimized Index",
            "problem": "Database queries are slow on large datasets",
            "algorithm": "Use adaptive B-tree with machine learning",
            "pseudocode": "def optimized_search(data, key): return ml_enhanced_btree(data, key)",
            "domain_relevance": 0.75
        }, indent=2)

    def _mock_code(self) -> str:
        """Return mock benchmark code."""
        return '''
import pytest

def test_optimized_index():
    """Test optimized index performance."""
    data = list(range(100000))

    # Mock optimized implementation
    start = time.time()
    result = optimized_lookup(data, 50000)
    elapsed = time.time() - start

    assert result == 50000
    assert elapsed < 0.01  # Should be very fast

    print(f"Lookup completed in {elapsed:.6f}s")
    return True
'''

    def embed(self, text: str) -> List[float]:
        """Return mock embedding vector."""
        # Return deterministic 384-dim vector
        return [0.1] * 384


class MockDockerSandbox:
    """Mock Docker sandbox for code execution."""

    def __init__(self):
        self.containers_created = 0
        self.containers_removed = 0

    def run_code(self, code: str, timeout: int = 60) -> MockResult:
        """Mock code execution in sandbox."""
        self.containers_created += 1
        logger.info(f"Mock sandbox: Would execute code in {len(code)} characters")

        # Simulate benchmark execution time
        time.sleep(0.01)  # Very fast mock

        return MockResult(
            success=True,
            data={
                "exit_code": 0,
                "stdout": "Mock benchmark output:\nops_per_sec: 1500.0\nlatency_p50: 0.001\nlatency_p99: 0.005\n",
                "stderr": "",
                "execution_time": 0.01
            },
            message="Code executed successfully (mock)"
        )

    def cleanup(self):
        """Mock cleanup."""
        self.containers_removed += 1


class MockRLPolicy:
    """Mock RL policy for paper selection."""

    def __init__(self):
        self.predict_count = 0

    def predict(self, observation: Any, deterministic: bool = True) -> tuple:
        """Return mock action."""
        self.predict_count += 1
        # Always return action 1 (process the paper)
        return 1, {}

    def train(self, total_timesteps: int) -> MockResult:
        """Mock training."""
        logger.info(f"Mock RL training: {total_timesteps} timesteps")
        return MockResult(success=True, message="Mock training completed")


class MockLoRATrainer:
    """Mock LoRA trainer for fine-tuning."""

    def __init__(self):
        self.train_count = 0

    def train(self, lessons: List[Dict]) -> MockResult:
        """Mock fine-tuning."""
        self.train_count += 1
        logger.info(f"Mock LoRA training: {len(lessons)} lessons")
        return MockResult(
            success=True,
            data={"adapter_path": "/tmp/mock_adapter_v1"},
            message="Mock fine-tuning completed"
        )


def is_mock_mode_enabled() -> bool:
    """Check if mock mode is enabled via environment variable."""
    import os
    return os.getenv("PERPETUAL_SCHOLAR_MOCK", "").lower() in ("1", "true", "yes")


def init_mock_mode():
    """Initialize mock mode and log warning."""
    if is_mock_mode_enabled():
        logger.warning("=" * 70)
        logger.warning("RUNNING IN MOCK MODE")
        logger.warning("All ML operations (LLM, FAISS, Docker, RL, LoRA) are mocked")
        logger.warning("No real model training or execution will occur")
        logger.warning("Set PERPETUAL_SCHOLAR_MOCK=0 to disable")
        logger.warning("=" * 70)
        return True
    return False


def get_mock_component(component_type: str) -> Any:
    """Get mock component by type."""
    components = {
        "faiss": MockFAISSIndex(),
        "llm": MockLLMBackend(),
        "docker": MockDockerSandbox(),
        "rl": MockRLPolicy(),
        "lora": MockLoRATrainer()
    }
    return components.get(component_type)


def mock_pipeline_cycle() -> Dict[str, Any]:
    """Run a complete mock pipeline cycle.

    Returns a mock result that matches the real pipeline structure.
    """
    logger.info("Running mock pipeline cycle...")

    # Simulate processing time
    time.sleep(0.1)

    # Return mock result matching real pipeline structure
    return {
        "papers_processed": 3,
        "papers_filtered": 1,
        "experiments_run": 2,
        "experiments_failed": 0,
        "lessons_stored": 1,
        "lessons_discarded": 1,
        "avg_reward": 0.5,
        "total_time_seconds": 0.1,
        "mock_mode": True
    }
