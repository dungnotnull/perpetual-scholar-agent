"""Reasoning pipeline: LLM-based paper summarizer."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class TechniqueSummary:
    """Structured summary of a research technique extracted from a paper."""
    technique_name: str = ""
    problem_solved: str = ""
    algorithm_description: str = ""
    pseudocode: str = ""
    key_findings: str = ""
    applicability: str = ""  # How applicable to our domain focus
    confidence: float = 0.0  # 0-1 confidence score from LLM


SYSTEM_PROMPT_SUMMARIZER = """You are an expert research analyst specializing in {domain_focus}.

Given a research paper title and abstract, extract:
1. **Technique Name**: A concise name for the technique or method proposed.
2. **Problem Solved**: What specific problem does this technique address?
3. **Algorithm Description**: How does the technique work? Be specific about the approach.
4. **Pseudocode**: Provide high-level pseudocode for the core algorithm.
5. **Key Findings**: What are the main experimental results?
6. **Applicability**: How applicable is this to backend performance optimization? Rate 0-1.
7. **Confidence**: How confident are you in this extraction? Rate 0-1.

Respond in JSON format with keys: technique_name, problem_solved, algorithm_description, pseudocode, key_findings, applicability, confidence."""


async def summarize_paper(
    title: str,
    abstract: str,
    url: str = "",
    llm_provider: Optional[str] = None,
) -> TechniqueSummary:
    """Summarize a research paper using the configured LLM.

    Args:
        title: Paper title.
        abstract: Paper abstract text.
        url: Paper URL (for context).
        llm_provider: Override LLM provider. Defaults to settings.

    Returns:
        TechniqueSummary with extracted information.
    """
    import json

    from agent.llm.backend import generate

    system_prompt = SYSTEM_PROMPT_SUMMARIZER.format(
        domain_focus=settings.domain_focus
    )

    user_prompt = f"""Title: {title}
Abstract: {abstract}
URL: {url}

Extract the technique summary as JSON."""

    try:
        response = await generate(user_prompt, system=system_prompt, provider=llm_provider)

        # Try to parse JSON from response
        # LLM may wrap in markdown code blocks
        json_str = response.strip()
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0].strip()

        data = json.loads(json_str)
        return TechniqueSummary(
            technique_name=data.get("technique_name", ""),
            problem_solved=data.get("problem_solved", ""),
            algorithm_description=data.get("algorithm_description", ""),
            pseudocode=data.get("pseudocode", ""),
            key_findings=data.get("key_findings", ""),
            applicability=data.get("applicability", ""),
            confidence=float(data.get("confidence", 0.0)),
        )

    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Failed to parse LLM summary as JSON: {e}")
        return TechniqueSummary(
            technique_name=title[:100],
            problem_solved=abstract[:500],
            algorithm_description="",
            pseudocode="",
            key_findings="",
            applicability="",
            confidence=0.3,  # Low confidence for unstructured responses
        )
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return TechniqueSummary(confidence=0.0)
