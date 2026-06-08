"""LLM backend: Anthropic Claude API client with retry logic."""
from __future__ import annotations

import logging
from typing import Optional

from agent.config.settings import settings
from agent.resilience import retry_llm

logger = logging.getLogger(__name__)


class ClaudeBackend:
    """Async Anthropic Claude API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
    ):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.claude_model
        self.max_retries = max_retries

        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be set to use Claude backend")

    @retry_llm
    async def generate(self, prompt: str, system: str = "", max_tokens: int = 2048, temperature: float = 0.3) -> str:
        """Generate text using Claude API.

        Args:
            prompt: User prompt.
            system: System prompt.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.

        Returns:
            Generated text string.
        """
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self.api_key)

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        response = await client.messages.create(**kwargs)
        return response.content[0].text

    @retry_llm
    async def judge_code(self, code: str, technique_description: str) -> dict:
        """Use Claude to evaluate code quality on multiple dimensions.

        Args:
            code: The Python code to evaluate.
            technique_description: What technique the code implements.

        Returns:
            Dict with correctness, readability, safety, performance, overall_score.
        """
        import json

        judge_prompt = f"""Technique: {technique_description}

Code to evaluate:
```python
{code[:3000]}
```

Rate this code on correctness, readability, safety, and performance (0-10 each).
Provide an overall_score (0-10) and brief reasoning.
Respond ONLY in JSON format with keys: correctness, readability, safety, performance, overall_score, reasoning."""

        system_prompt = "You are a code quality evaluator. Always respond in valid JSON format."

        response = await self.generate(judge_prompt, system=system_prompt, temperature=0.1)

        try:
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0].strip()
            return json.loads(json_str)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to parse Claude judge response as JSON: {e}")
            return {
                "correctness": 0, "readability": 0, "safety": 0,
                "performance": 0, "overall_score": 0,
                "reasoning": f"Parse error: {e}",
            }
