"""LLM backend: unified async interface with fallback chain and retry logic."""
from __future__ import annotations

import logging
from typing import Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


async def generate(
    prompt: str,
    system: str = "",
    provider: Optional[str] = None,
    max_tokens: int = 2048,
    temperature: float = 0.3,
) -> str:
    """Generate text using the configured LLM provider with automatic fallback.

    Tries providers in order according to the fallback chain setting.
    Returns the first successful response.

    Args:
        prompt: User prompt text.
        system: System prompt text.
        provider: Override provider ("ollama", "claude", "openai").
        max_tokens: Maximum tokens to generate.
        temperature: Sampling temperature.

    Returns:
        Generated text string.

    Raises:
        RuntimeError: If all providers fail.
    """
    chain = [provider] if provider else settings.fallback_chain_list

    last_error = None
    for p in chain:
        try:
            logger.debug(f"trying_llm_provider", extra={"provider": p})

            if p == "ollama":
                from agent.llm.ollama_backend import OllamaBackend
                backend = OllamaBackend()
                return await backend.generate(prompt, system, max_tokens, temperature)

            elif p == "claude":
                from agent.llm.claude_backend import ClaudeBackend
                backend = ClaudeBackend()
                return await backend.generate(prompt, system, max_tokens, temperature)

            elif p == "openai":
                from agent.llm.openai_backend import OpenAIBackend
                backend = OpenAIBackend()
                return await backend.generate(prompt, system, max_tokens, temperature)

            else:
                logger.warning(f"unknown_provider", extra={"provider": p})
                continue

        except Exception as e:
            logger.warning(f"provider_failed", extra={"provider": p, "error": str(e)})
            last_error = e
            continue

    raise RuntimeError(f"All LLM providers failed. Last error: {last_error}")


async def judge_code_quality(
    code: str,
    technique_description: str,
    provider: Optional[str] = None,
) -> dict:
    """Evaluate code quality using the best available LLM judge.

    Uses Claude (preferred for judgment) if available, otherwise falls back
    to the configured provider chain.

    Args:
        code: The Python code to evaluate.
        technique_description: Description of the technique.
        provider: Override provider.

    Returns:
        Dict with quality scores.
    """
    import json

    from agent.reasoning.prompts import LLM_JUDGE_SYSTEM_PROMPT

    # Prefer Claude for judgment tasks
    judge_provider = provider or ("claude" if settings.anthropic_api_key else settings.llm_provider)

    user_prompt = f"""Technique: {technique_description}

Code to evaluate:
```python
{code[:3000]}
```

Rate this code on correctness, readability, safety, and performance (0-10 each).
Provide an overall_score (0-10) and brief reasoning.
Respond ONLY in JSON format with keys: correctness, readability, safety, performance, overall_score, reasoning."""

    try:
        if judge_provider == "claude":
            from agent.llm.claude_backend import ClaudeBackend
            backend = ClaudeBackend()
            return await backend.judge_code(code, technique_description)

        response = await generate(user_prompt, system=LLM_JUDGE_SYSTEM_PROMPT, provider=judge_provider, temperature=0.1)

        json_str = response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        return json.loads(json_str)

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"judge_response_parse_failed", extra={"error": str(e)})
        return {
            "correctness": 0, "readability": 0, "safety": 0,
            "performance": 0, "overall_score": 0,
            "reasoning": f"Parse error: {e}",
        }
    except Exception as e:
        logger.error(f"judge_failed", extra={"error": str(e)})
        return {
            "correctness": 0, "readability": 0, "safety": 0,
            "performance": 0, "overall_score": 0,
            "reasoning": f"Error: {e}",
        }
