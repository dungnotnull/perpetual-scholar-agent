"""
Mock implementations for testing.

Provides mock versions of external dependencies (Ollama, Claude API, Docker)
to enable fast, deterministic unit tests without external service calls.
"""

from typing import Any, Dict, List, Optional
from unittest.mock import Mock, MagicMock
from datetime import datetime
import json


class MockOllamaBackend:
    """Mock Ollama backend for testing LLM interactions."""

    def __init__(self, responses: Optional[Dict[str, str]] = None):
        """
        Initialize mock Ollama backend.

        Args:
            responses: Dict mapping operation types to mock responses
        """
        self.responses = responses or {
            "generate": self._default_generate_response,
            "chat": "I can help with that query.",
            "embed": [0.1] * 384  # Mock embedding vector
        }
        self.call_count = 0
        self.call_history = []
        self.models = ["qwen2.5-coder:7b", "deepseek-coder:7b"]
        self.current_model = "qwen2.5-coder:7b"

    def _default_generate_response(self, prompt: str) -> str:
        """Generate mock code response based on prompt keywords."""
        if "function" in prompt.lower() or "def" in prompt.lower():
            return """
def example_function(input_data):
    '''Example generated function'''
    result = process(input_data)
    return result
"""
        elif "class" in prompt.lower():
            return """
class ExampleClass:
    '''Example generated class'''
    def __init__(self, value):
        self.value = value

    def process(self):
        return self.value * 2
"""
        else:
            return "# Mock generated code\nprint('Hello, world!')"

    def generate(self, prompt: str, **kwargs) -> str:
        """Mock code generation."""
        self.call_count += 1
        self.call_history.append(("generate", prompt, kwargs))
        response = self.responses["generate"]
        if callable(response):
            return response(prompt)
        return response

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Mock chat completion."""
        self.call_count += 1
        self.call_history.append(("chat", messages, kwargs))
        return self.responses["chat"]

    def embed(self, text: str, **kwargs) -> List[float]:
        """Mock text embedding."""
        self.call_count += 1
        self.call_history.append(("embed", text, kwargs))
        return self.responses["embed"]

    def list_models(self) -> List[str]:
        """Mock model listing."""
        return self.models

    def set_model(self, model: str) -> None:
        """Mock model switching."""
        if model in self.models:
            self.current_model = model
        else:
            raise ValueError(f"Model {model} not available")

    def reset(self) -> None:
        """Reset call tracking."""
        self.call_count = 0
        self.call_history = []


class MockClaudeBackend:
    """Mock Claude API backend for testing."""

    def __init__(self, api_key: str = "test-api-key"):
        """Initialize mock Claude backend."""
        self.api_key = api_key
        self.messages = []
        self.responses = []
        self.call_count = 0
        self.total_tokens_used = 0

    def message(self, content: str, **kwargs) -> str:
        """Mock message completion."""
        self.call_count += 1
        self.messages.append(content)
        self.total_tokens_used += len(content.split())

        response = self._generate_mock_response(content)
        self.responses.append(response)
        return response

    def _generate_mock_response(self, content: str) -> str:
        """Generate contextual mock response."""
        content_lower = content.lower()

        if "summarize" in content_lower and "paper" in content_lower:
            return """This paper presents a novel approach to optimizing database query performance through intelligent indexing strategies. The authors demonstrate a 35% reduction in query latency on standard benchmarks. Key contributions include: (1) adaptive index selection, (2) machine learning-driven query optimization, and (3) automatic performance tuning."""

        elif "analyze" in content_lower or "explain" in content_lower:
            return """The code implements a caching layer that reduces redundant database calls. It uses a least-recently-used (LRU) eviction policy and supports TTL-based expiration. The implementation is thread-safe and handles cache misses gracefully."""

        else:
            return "Based on the analysis, the recommended approach involves refactoring the database access layer to use prepared statements and implementing connection pooling for better performance."

    def get_usage_stats(self) -> Dict[str, int]:
        """Get mock usage statistics."""
        return {
            "call_count": self.call_count,
            "total_tokens": self.total_tokens_used,
            "average_tokens": self.total_tokens_used // max(self.call_count, 1)
        }

    def reset(self) -> None:
        """Reset tracking."""
        self.messages = []
        self.responses = []
        self.call_count = 0
        self.total_tokens_used = 0


class MockDockerClient:
    """Mock Docker client for testing sandbox execution."""

    def __init__(self):
        """Initialize mock Docker client."""
        self.containers = {}
        self.images = []
        self.networks = {}
        self.volumes = {}
        self._container_id_counter = 0

    def _generate_container_id(self) -> str:
        """Generate unique container ID."""
        self._container_id_counter += 1
        return f"mock-container-{self._container_id_counter}"

    def containers_create(self, image: str, command: Optional[str] = None,
                         **kwargs) -> Mock:
        """Mock container creation."""
        container_id = self._generate_container_id()
        container = Mock()
        container.id = container_id
        container.image = image
        container.command = command
        container.status = "created"
        container.logs = []
        container.exit_code = 0
        container.output = ""
        container.error = ""

        # Apply configuration
        for key, value in kwargs.items():
            setattr(container, key, value)

        self.containers[container_id] = container
        return container

    def containers_get(self, container_id: str) -> Optional[Mock]:
        """Get container by ID."""
        return self.containers.get(container_id)

    def containers_start(self, container_id: str) -> None:
        """Mock container start."""
        container = self.containers.get(container_id)
        if container:
            container.status = "running"

    def containers_stop(self, container_id: str, **kwargs) -> None:
        """Mock container stop."""
        container = self.containers.get(container_id)
        if container:
            container.status = "exited"

    def containers_remove(self, container_id: str, **kwargs) -> None:
        """Mock container removal."""
        if container_id in self.containers:
            del self.containers[container_id]

    def containers_wait(self, container_id: str, timeout: Optional[int] = None) -> Dict[str, Any]:
        """Mock container wait."""
        container = self.containers.get(container_id)
        if container:
            return {
                "StatusCode": container.exit_code,
                "Error": container.error
            }
        return {"StatusCode": -1, "Error": "Container not found"}

    def containers_logs(self, container_id: str, **kwargs) -> str:
        """Mock container logs."""
        container = self.containers.get(container_id)
        if container:
            return container.output
        return ""

    def images_pull(self, image: str) -> Mock:
        """Mock image pull."""
        mock_image = Mock()
        mock_image.id = f"sha256:{hash(image)}"
        mock_image.tags = [image]
        self.images.append(mock_image)
        return mock_image

    def networks_create(self, name: str, **kwargs) -> Mock:
        """Mock network creation."""
        network = Mock()
        network.id = f"network-{name}"
        network.name = name
        self.networks[name] = network
        return network

    def volumes_create(self, name: str, **kwargs) -> Mock:
        """Mock volume creation."""
        volume = Mock()
        volume.id = f"volume-{name}"
        volume.name = name
        self.volumes[name] = volume
        return volume

    def ping(self) -> bool:
        """Mock Docker daemon ping."""
        return True

    def reset(self) -> None:
        """Reset all state."""
        self.containers = {}
        self.images = []
        self.networks = {}
        self.volumes = {}
        self._container_id_counter = 0


class MockDatabase:
    """Mock database for testing persistence operations."""

    def __init__(self):
        """Initialize mock database."""
        self.tables = {
            "lessons": [],
            "experiments": [],
            "papers": [],
            "metrics": []
        }
        self.transactions = []

    def insert(self, table: str, record: Dict[str, Any]) -> str:
        """Mock insert operation."""
        if table not in self.tables:
            raise ValueError(f"Table {table} does not exist")

        record_id = record.get("id", f"{table}-{len(self.tables[table]) + 1}")
        record_with_id = {**record, "id": record_id, "created_at": datetime.utcnow()}
        self.tables[table].append(record_with_id)
        return record_id

    def select(self, table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Mock select operation."""
        if table not in self.tables:
            raise ValueError(f"Table {table} does not exist")

        records = self.tables[table]

        if filters:
            return [
                r for r in records
                if all(r.get(k) == v for k, v in filters.items())
            ]

        return records.copy()

    def update(self, table: str, record_id: str, updates: Dict[str, Any]) -> bool:
        """Mock update operation."""
        if table not in self.tables:
            raise ValueError(f"Table {table} does not exist")

        for i, record in enumerate(self.tables[table]):
            if record.get("id") == record_id:
                self.tables[table][i] = {**record, **updates, "updated_at": datetime.utcnow()}
                return True
        return False

    def delete(self, table: str, record_id: str) -> bool:
        """Mock delete operation."""
        if table not in self.tables:
            raise ValueError(f"Table {table} does not exist")

        original_length = len(self.tables[table])
        self.tables[table] = [r for r in self.tables[table] if r.get("id") != record_id]
        return len(self.tables[table]) < original_length

    def count(self, table: str) -> int:
        """Mock count operation."""
        return len(self.tables.get(table, []))

    def begin_transaction(self) -> str:
        """Mock transaction begin."""
        transaction_id = f"txn-{len(self.transactions)}"
        self.transactions.append(transaction_id)
        return transaction_id

    def commit(self, transaction_id: str) -> bool:
        """Mock transaction commit."""
        return transaction_id in self.transactions

    def rollback(self, transaction_id: str) -> bool:
        """Mock transaction rollback."""
        if transaction_id in self.transactions:
            self.transactions.remove(transaction_id)
            return True
        return False

    def reset(self) -> None:
        """Reset database state."""
        self.tables = {
            "lessons": [],
            "experiments": [],
            "papers": [],
            "metrics": []
        }
        self.transactions = []


class MockRedis:
    """Mock Redis client for testing caching operations."""

    def __init__(self):
        """Initialize mock Redis."""
        self.store = {}
        self.expirations = {}
        self.lists = {}
        self.sets = {}

    def get(self, key: str) -> Optional[str]:
        """Mock get operation."""
        if key in self.expirations:
            import time
            if time.time() > self.expirations[key]:
                del self.store[key]
                del self.expirations[key]
                return None
        return self.store.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Mock set operation."""
        self.store[key] = value
        if ex:
            import time
            self.expirations[key] = time.time() + ex
        return True

    def delete(self, *keys: str) -> int:
        """Mock delete operation."""
        count = 0
        for key in keys:
            if key in self.store:
                del self.store[key]
                count += 1
        return count

    def exists(self, key: str) -> bool:
        """Mock exists operation."""
        return key in self.store

    def lpush(self, key: str, *values: str) -> int:
        """Mock list push operation."""
        if key not in self.lists:
            self.lists[key] = []
        self.lists[key] = list(reversed(values)) + self.lists[key]
        return len(self.lists[key])

    def rpop(self, key: str) -> Optional[str]:
        """Mock list pop operation."""
        if key in self.lists and self.lists[key]:
            return self.lists[key].pop()
        return None

    def lrange(self, key: str, start: int, stop: int) -> List[str]:
        """Mock list range operation."""
        if key not in self.lists:
            return []
        if stop == -1:
            return self.lists[key][start:]
        return self.lists[key][start:stop + 1]

    def sadd(self, key: str, *members: str) -> int:
        """Mock set add operation."""
        if key not in self.sets:
            self.sets[key] = set()
        before = len(self.sets[key])
        self.sets[key].update(members)
        return len(self.sets[key]) - before

    def smembers(self, key: str) -> set:
        """Mock set members operation."""
        return self.sets.get(key, set()).copy()

    def flushdb(self) -> bool:
        """Mock database flush."""
        self.store = {}
        self.expirations = {}
        self.lists = {}
        self.sets = {}
        return True

    def reset(self) -> None:
        """Reset all state."""
        self.store = {}
        self.expirations = {}
        self.lists = {}
        self.sets = {}


class MockEmbeddingModel:
    """Mock embedding model for testing vector operations."""

    def __init__(self, embedding_dim: int = 384):
        """Initialize mock embedding model."""
        self.embedding_dim = embedding_dim
        self.call_count = 0

    def encode(self, texts: List[str], **kwargs) -> List[List[float]]:
        """Mock text encoding."""
        self.call_count += 1
        embeddings = []
        for text in texts:
            # Generate deterministic embeddings based on text hash
            import hashlib
            hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
            embedding = [(hash_value >> i) % 100 / 100.0 for i in range(self.embedding_dim)]
            embeddings.append(embedding)
        return embeddings

    def encode_single(self, text: str) -> List[float]:
        """Mock single text encoding."""
        return self.encode([text])[0]

    def reset(self) -> None:
        """Reset call tracking."""
        self.call_count = 0


# Factory functions for creating configured mocks

def create_mock_ollama(responses: Optional[Dict[str, str]] = None) -> MockOllamaBackend:
    """Create configured mock Ollama backend."""
    return MockOllamaBackend(responses)


def create_mock_claude(api_key: str = "test-key") -> MockClaudeBackend:
    """Create configured mock Claude backend."""
    return MockClaudeBackend(api_key)


def create_mock_docker() -> MockDockerClient:
    """Create configured mock Docker client."""
    return MockDockerClient()


def create_mock_database() -> MockDatabase:
    """Create configured mock database."""
    return MockDatabase()


def create_mock_redis() -> MockRedis:
    """Create configured mock Redis client."""
    return MockRedis()


def create_mock_embedding_model(embedding_dim: int = 384) -> MockEmbeddingModel:
    """Create configured mock embedding model."""
    return MockEmbeddingModel(embedding_dim)
