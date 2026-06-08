"""Reward engine: benchmark reward calculator."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from agent.config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class RewardResult:
    """Computed reward for an experiment."""
    benchmark_reward: float        # (new - baseline) / baseline
    llm_judge_score: float = 0.0   # 0-10 scale from LLM judge
    combined_reward: float = 0.0   # weighted combination
    improvement_pct: float = 0.0   # percentage improvement
    is_positive: bool = False       # True if improvement > threshold
    is_negative: bool = False      # True if degradation > threshold


def calculate_benchmark_reward(
    new_metric: float,
    baseline_metric: float,
) -> float:
    """Calculate the raw benchmark reward.

    reward = (new_metric - baseline_metric) / baseline_metric

    Clamped to [-1.0, +1.0] to prevent extreme values.

    Args:
        new_metric: The technique's metric (e.g., ops/sec).
        baseline_metric: The baseline metric.

    Returns:
        Float reward in [-1.0, +1.0].
    """
    if baseline_metric == 0:
        logger.warning("Baseline metric is zero — returning reward of 0.0")
        return 0.0

    reward = (new_metric - baseline_metric) / baseline_metric
    return max(-1.0, min(1.0, reward))


def calculate_combined_reward(
    benchmark_reward: float,
    llm_judge_score: float = 0.0,
    benchmark_weight: Optional[float] = None,
    llm_weight: Optional[float] = None,
) -> float:
    """Calculate the combined reward from benchmark and LLM judge.

    combined = benchmark_weight * benchmark_reward + llm_weight * (llm_score / 10)

    Args:
        benchmark_reward: Raw benchmark reward in [-1, 1].
        llm_judge_score: LLM judge score in [0, 10].
        benchmark_weight: Weight for benchmark. Defaults to settings.
        llm_weight: Weight for LLM judge. Defaults to settings.

    Returns:
        Combined reward in approximately [-1, 1].
    """
    bw = benchmark_weight or settings.reward_benchmark_weight
    lw = llm_weight or settings.reward_llm_judge_weight
    normalized_llm = llm_judge_score / 10.0  # scale to [0, 1]
    return bw * benchmark_reward + lw * normalized_llm


def compute_reward(
    new_metric: float,
    baseline_metric: float,
    llm_judge_score: float = 0.0,
) -> RewardResult:
    """Full reward computation for an experiment.

    Args:
        new_metric: Technique benchmark metric (ops/sec).
        baseline_metric: Baseline benchmark metric (ops/sec).
        llm_judge_score: Optional LLM judge quality score [0-10].

    Returns:
        RewardResult with all computed fields.
    """
    benchmark_reward = calculate_benchmark_reward(new_metric, baseline_metric)
    combined_reward = calculate_combined_reward(benchmark_reward, llm_judge_score)
    improvement_pct = (new_metric - baseline_metric) / baseline_metric * 100 if baseline_metric > 0 else 0.0

    return RewardResult(
        benchmark_reward=benchmark_reward,
        llm_judge_score=llm_judge_score,
        combined_reward=combined_reward,
        improvement_pct=improvement_pct,
        is_positive=benchmark_reward > settings.reward_improvement_threshold,
        is_negative=benchmark_reward < settings.reward_degradation_threshold,
    )
