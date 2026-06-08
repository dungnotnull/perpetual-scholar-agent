"""LLM backend: Ollama-specific client with retry logic."""
from __future__ import annotations

import logging
from typing import Optional

import httpx

from agent.config.settings import settings
from agent.resilience import retry_llm

logger = logging.getLogger(__name__)


class OllamaBackend:
    """Synchronous and asynchronous Ollama API client."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 180.0,
    ):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.ollama_model
        self.timeout = timeout

    def healthcheck(self) -> bool:
        """Check if Ollama server is responding."""
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            return False

    def list_models(self) -> list[str]:
        """List locally available models."""
        try:
            resp = httpx.get(f"{self.base_url}/api/tags", timeout=10.0)
            resp.raise_for_status()
            data = resp.json()
            return [m.get("name", "") for m in data.get("models", [])]
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {e}")
            return []

    def pull_model(self, model: Optional[str] = None) -> bool:
        """Pull a model via Ollama API."""
        model = model or self.model
        try:
            resp = httpx.post(
                f"{self.base_url}/api/pull",
                json={"name": model, "stream": False},
                timeout=600.0,
            )
            resp.raise_for_status()
            logger.info(f"Model '{model}' pulled successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to pull model '{model}': {e}")
            return False

    @retry_llm
    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048, temperature: float = 0.3) -> str:
        """Generate text using Ollama.

        Args:
            prompt: User prompt.
            system: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            Generated text string.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            },
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")

    @retry_llm
    async def embeddings(self, prompt: str) -> list[float]:
        """Generate embeddings using Ollama.

        Args:
            prompt: Text to embed.

        Returns:
            List of float embeddings.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/embeddings", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [])
