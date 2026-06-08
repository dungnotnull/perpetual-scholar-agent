"""LLM backend: OpenAI GPT API client with retry logic."""
from __future__ import annotations

import logging
from typing import Optional

from agent.config.settings import settings
from agent.resilience import retry_llm

logger = logging.getLogger(__name__)


class OpenAIBackend:
    """Async OpenAI GPT API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.gpt_model

        if not self.api_key:
            raise ValueError("OPENAI_API_KEY must be set to use OpenAI backend")

    @retry_llm
    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048, temperature: float = 0.3) -> str:
        """Generate text using OpenAI GPT API.

        Args:
            prompt: User prompt.
            system: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            Generated text string.
        """
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=messages,
        )
        return response.choices[0].message.content or ""
