"""Reasoning pipeline: LLM-based code generator."""
from __future__ import annotations

import logging
from typing import List, Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


SYSTEM_PROMPT_CODE_GEN = """You are an expert Python developer specializing in {domain_focus}.

Your task is to write a self-contained Python benchmark test file that demonstrates a specific technique.

Requirements:
1. The file must be a valid pytest-benchmark test file.
2. Include a baseline implementation and the new technique implementation.
3. Use pytest-benchmark's `benchmark` fixture to measure both.
4. The file must run with: python -m pytest --benchmark-only --benchmark-json=results.json
5. Include clear docstrings explaining the technique.
6. Do NOT use any external dependencies beyond Python stdlib.
7. The technique function should be named `technique_*` and the baseline `baseline_*`.
8. Include assertions to verify correctness (not just speed).
9. Output ONLY the Python code, no markdown fences, no explanation.

Write production-quality, well-commented code."""


async def generate_benchmark_code(
    technique_name: str,
    problem_solved: str,
    algorithm_description: str,
    pseudocode: str = "",
    context_lessons: Optional[List[str]] = None,
    llm_provider: Optional[str] = None,
) -> str:
    """Generate runnable Python benchmark code from a technique summary.

    Args:
        technique_name: Name of the technique.
        problem_solved: What problem the technique addresses.
        algorithm_description: How the technique works.
        pseudocode: Optional pseudocode from the paper.
        context_lessons: Optional list of verified lesson code snippets for few-shot context.
        llm_provider: Override LLM provider.

    Returns:
        String of Python benchmark code.
    """
    from agent.llm.backend import generate

    system_prompt = SYSTEM_PROMPT_CODE_GEN.format(domain_focus=settings.domain_focus)

    user_parts = [
        f"Technique: {technique_name}",
        f"Problem: {problem_solved}",
        f"Algorithm: {algorithm_description}",
    ]
    if pseudocode:
        user_parts.append(f"Pseudocode:\n{pseudocode}")

    if context_lessons:
        user_parts.append("Reference implementations (verified techniques):")
        for i, lesson in enumerate(context_lessons[:3]):  # max 3 few-shot examples
            user_parts.append(f"--- Example {i+1} ---\n{lesson[:500]}")

    user_parts.append(
        "Write a complete pytest-benchmark test file with a baseline and technique implementation."
    )

    user_prompt = "\n\n".join(user_parts)

    try:
        response = await generate(user_prompt, system=system_prompt, provider=llm_provider)

        # Clean up markdown fences if present
        code = response.strip()
        if code.startswith("```python"):
            code = code[len("```python"):].strip()
        if code.startswith("```"):
            code = code[3:].strip()
        if code.endswith("```"):
            code = code[:-3].strip()

        return code

    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        return ""
