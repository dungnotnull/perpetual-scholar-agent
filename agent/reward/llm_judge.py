"""Reward engine: LLM judge for code quality scoring with fallback chain."""
from __future__ import annotations

import json
import logging
from typing import Optional

from agent.config.settings import settings
from agent.reasoning.prompts import LLM_JUDGE_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


async def judge_code_quality(
    code: str,
    technique_description: str,
    llm_provider: Optional[str] = None,
) -> dict:
    """Use an LLM to judge code quality on multiple dimensions.

    Uses the unified LLM backend with fallback chain. Prefers Claude
    for judgment tasks when available.

    Args:
        code: The Python code to evaluate.
        technique_description: What technique the code implements.
        llm_provider: Override LLM provider.

    Returns:
        Dict with keys: correctness, readability, safety, performance,
        overall_score (0-10), reasoning.
    """
    from agent.llm.backend import generate

    user_prompt = f"""Technique: {technique_description}

Code to evaluate:
```python
{code[:3000]}
```

Rate this code on correctness, readability, safety, and performance (0-10 each).
Provide an overall_score (0-10) and brief reasoning.
Respond ONLY in JSON format with keys: correctness, readability, safety, performance, overall_score, reasoning."""

    # Prefer Claude for judgment if available
    provider = llm_provider
    if provider is None:
        if settings.anthropic_api_key:
            provider = "claude"

    try:
        response = await generate(
            user_prompt,
            system=LLM_JUDGE_SYSTEM_PROMPT,
            provider=provider,
            max_tokens=512,
            temperature=0.1,
        )

        json_str = response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        result = json.loads(json_str)
        return {
            "correctness": float(result.get("correctness", 0)),
            "readability": float(result.get("readability", 0)),
            "safety": float(result.get("safety", 0)),
            "performance": float(result.get("performance", 0)),
            "overall_score": float(result.get("overall_score", 0)),
            "reasoning": result.get("reasoning", ""),
        }

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
