"""
Unit tests for reward calculator module.

Tests reward calculation logic including improvement/degradation detection,
benchmark weighting, and LLM judge scoring.
"""

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch

from agent.reward.calculator import RewardCalculator


class TestRewardCalculatorInitialization:
    """Test reward calculator initialization."""

    def test_default_initialization(self):
        """Test default calculator initialization."""
        calculator = RewardCalculator()
        assert calculator is not None

    def test_custom_thresholds(self):
        """Test custom improvement/degradation thresholds."""
        calculator = RewardCalculator(
            improvement_threshold=0.1,
            degradation_threshold=-0.1
        )
        assert calculator.improvement_threshold == 0.1
        assert calculator.degradation_threshold == -0.1

    def test_custom_weights(self):
        """Test custom LLM and benchmark weights."""
        calculator = RewardCalculator(
            llm_weight=0.4,
            benchmark_weight=0.6
        )
        assert calculator.llm_weight == 0.4
        assert calculator.benchmark_weight == 0.6

    def test_weights_sum_to_one(self):
        """Test weights sum to 1.0."""
        calculator = RewardCalculator(
            llm_weight=0.3,
            benchmark_weight=0.7
        )
        total = calculator.llm_weight + calculator.benchmark_weight
        assert abs(total - 1.0) < 0.01


class TestRewardCalculationBasic:
    """Test basic reward calculation logic."""

    @pytest.fixture
    def calculator(self):
        """Provide calculator with default settings."""
        return RewardCalculator(
            improvement_threshold=0.05,
            degradation_threshold=-0.05,
            llm_weight=0.3,
            benchmark_weight=0.7
        )

    def test_positive_reward_for_improvement(self, calculator):
        """Test positive reward for significant improvement."""
        baseline = 100.0
        experiment = 135.0  # 35% improvement

        reward = calculator.calculate(baseline, experiment)

        assert reward > 0
        assert reward <= 1.0

    def test_negative_reward_for_degradation(self, calculator):
        """Test negative reward for significant degradation."""
        baseline = 100.0
        experiment = 85.0  # 15% degradation

        reward = calculator.calculate(baseline, experiment)

        assert reward < 0
        assert reward >= -1.0

    def test_zero_reward_for_no_change(self, calculator):
        """Test zero reward for no significant change."""
        baseline = 100.0
        experiment = 102.0  # 2% improvement (below threshold)

        reward = calculator.calculate(baseline, experiment)

        assert reward == 0

    def test_handles_zero_baseline(self, calculator):
        """Test handling zero baseline value."""
        baseline = 0.0
        experiment = 10.0

        # Should handle gracefully, either return 0 or raise specific error
        try:
            reward = calculator.calculate(baseline, experiment)
            assert isinstance(reward, (int, float))
        except ZeroDivisionError:
            # Expected behavior for zero baseline
            pass

    def test_handles_negative_values(self, calculator):
        """Test handling negative metric values."""
        baseline = -100.0  # e.g., latency reduction
        experiment = -135.0  # Further reduction (improvement)

        reward = calculator.calculate(baseline, experiment)

        # Should handle based on context (lower is better or higher is better)
        assert isinstance(reward, (int, float))


class TestRewardCalculationScenarios:
    """Test realistic reward calculation scenarios."""

    @pytest.fixture
    def calculator(self):
        """Provide calculator instance."""
        return RewardCalculator()

    def test_throughput_improvement(self, calculator):
        """Test reward for throughput improvement."""
        # Higher is better
        baseline = 1000  # requests per minute
        experiment = 1200  # 20% improvement

        reward = calculator.calculate(baseline, experiment)

        assert reward > 0

    def test_latency_improvement(self, calculator):
        """Test reward for latency improvement."""
        # Lower is better
        baseline = 100  # milliseconds
        experiment = 70  # 30% improvement

        # May need to specify direction
        reward = calculator.calculate(baseline, experiment, lower_is_better=True)

        assert reward > 0

    def test_memory_usage_reduction(self, calculator):
        """Test reward for memory usage reduction."""
        baseline = 512  # MB
        experiment = 400  # MB

        reward = calculator.calculate(baseline, experiment, lower_is_better=True)

        assert reward > 0

    def test_error_rate_improvement(self, calculator):
        """Test reward for error rate reduction."""
        baseline = 0.05  # 5% error rate
        experiment = 0.02  # 2% error rate

        reward = calculator.calculate(baseline, experiment, lower_is_better=True)

        assert reward > 0


class TestLLMJudgeScoring:
    """Test LLM judge contribution to reward."""

    @pytest.fixture
    def calculator(self):
        """Provide calculator instance."""
        return RewardCalculator(llm_weight=0.3, benchmark_weight=0.7)

    def test_llm_judge_positive_score(self, calculator):
        """Test positive LLM judge score."""
        llm_score = 0.8  # High quality code
        benchmark_score = 0.6  # Moderate improvement

        reward = calculator.calculate_with_judge(
            baseline=100.0,
            experiment=110.0,
            llm_judge_score=llm_score
        )

        # Should incorporate both scores
        assert reward > 0

    def test_llm_judge_negative_score(self, calculator):
        """Test negative LLM judge score."""
        llm_score = 0.2  # Low quality code
        benchmark_score = 0.8  # High improvement

        reward = calculator.calculate_with_judge(
            baseline=100.0,
            experiment=150.0,
            llm_judge_score=llm_score
        )

        # LLM judge should reduce reward
        assert reward > 0  # Still positive due to benchmark

    def test_llm_judge_only(self, calculator):
        """Test calculation with only LLM judge score."""
        calculator_only = RewardCalculator(llm_weight=1.0, benchmark_weight=0.0)

        reward = calculator_only.calculate_with_judge(
            baseline=100.0,
            experiment=100.0,
            llm_judge_score=0.7
        )

        assert reward == pytest.approx(0.7)


class TestBenchmarkScoring:
    """Test benchmark contribution to reward."""

    @pytest.fixture
    def calculator(self):
        """Provide calculator instance."""
        return RewardCalculator(llm_weight=0.3, benchmark_weight=0.7)

    def test_high_improvement_score(self, calculator):
        """Test high improvement score."""
        baseline = 100.0
        experiment = 150.0  # 50% improvement

        benchmark_score = calculator._calculate_benchmark_score(baseline, experiment)

        assert benchmark_score > 0.5  # High score for significant improvement

    def test_no_improvement_score(self, calculator):
        """Test no improvement score."""
        baseline = 100.0
        experiment = 101.0  # 1% improvement

        benchmark_score = calculator._calculate_benchmark_score(baseline, experiment)

        # Should be low or zero
        assert benchmark_score < 0.2

    def test_degradation_score(self, calculator):
        """Test degradation score."""
        baseline = 100.0
        experiment = 80.0  # 20% degradation

        benchmark_score = calculator._calculate_benchmark_score(baseline, experiment)

        assert benchmark_score < 0


class TestRewardStatistics:
    """Test reward calculation statistics."""

    def test_tracks_calculation_count(self):
        """Test tracking number of calculations."""
        calculator = RewardCalculator()

        for i in range(10):
            calculator.calculate(100.0, 100.0 + i)

        if hasattr(calculator, 'calculation_count'):
            assert calculator.calculation_count == 10

    def test_tracks_average_reward(self):
        """Test tracking average reward."""
        calculator = RewardCalculator()

        rewards = []
        for i in range(10):
            reward = calculator.calculate(100.0, 100.0 + i * 10)
            rewards.append(reward)

        if hasattr(calculator, 'average_reward'):
            expected = sum(rewards) / len(rewards)
            assert calculator.average_reward == pytest.approx(expected)

    def test_tracks_reward_distribution(self):
        """Test tracking reward distribution."""
        calculator = RewardCalculator()

        calculator.calculate(100.0, 150.0)  # Positive
        calculator.calculate(100.0, 80.0)   # Negative
        calculator.calculate(100.0, 102.0)  # Zero

        if hasattr(calculator, 'reward_distribution'):
            distribution = calculator.reward_distribution
            assert distribution['positive'] >= 1
            assert distribution['negative'] >= 1
            assert distribution['zero'] >= 1


class TestRewardCalculatorEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def calculator(self):
        """Provide calculator instance."""
        return RewardCalculator()

    def test_identical_values(self, calculator):
        """Test identical baseline and experiment values."""
        reward = calculator.calculate(100.0, 100.0)
        assert reward == 0

    def test_very_small_improvement(self, calculator):
        """Test very small improvement."""
        baseline = 100.0
        experiment = 100.001  # 0.001% improvement

        reward = calculator.calculate(baseline, experiment)
        assert reward == 0  # Below threshold

    def test_very_large_improvement(self, calculator):
        """Test very large improvement."""
        baseline = 100.0
        experiment = 10000.0  # 100x improvement

        reward = calculator.calculate(baseline, experiment)
        # Should cap at maximum reward
        assert reward <= 1.0

    def test_negative_to_positive(self, calculator):
        """Test negative to positive metric."""
        baseline = -100.0
        experiment = 100.0

        reward = calculator.calculate(baseline, experiment)
        assert isinstance(reward, (int, float))

    def test_infinite_values(self, calculator):
        """Test handling infinite values."""
        import math

        reward = calculator.calculate(100.0, math.inf)

        # Should handle gracefully
        assert isinstance(reward, (int, float)) or reward is None

    def test_nan_values(self, calculator):
        """Test handling NaN values."""
        import math

        reward = calculator.calculate(100.0, math.nan)

        # Should handle gracefully
        assert isinstance(reward, (int, float)) or reward is None


class TestRewardCalculatorConfiguration:
    """Test calculator configuration and validation."""

    def test_invalid_weight_sum(self):
        """Test invalid weight sum."""
        with pytest.raises(ValueError):
            RewardCalculator(llm_weight=0.8, benchmark_weight=0.5)  # Sum > 1.0

    def test_negative_weights(self):
        """Test negative weights."""
        with pytest.raises(ValueError):
            RewardCalculator(llm_weight=-0.1, benchmark_weight=1.1)

    def test_invalid_thresholds(self):
        """Test invalid threshold configuration."""
        with pytest.raises(ValueError):
            RewardCalculator(
                improvement_threshold=-0.1,
                degradation_threshold=0.1
            )


class TestRewardCalculatorIntegration:
    """Test calculator with realistic scenarios."""

    @pytest.fixture
    def realistic_calculator(self):
        """Provide calculator with production-like settings."""
        return RewardCalculator(
            improvement_threshold=0.05,
            degradation_threshold=-0.05,
            llm_weight=0.3,
            benchmark_weight=0.7
        )

    @pytest.fixture
    def realistic_experiment_result(self):
        """Provide realistic experiment result."""
        return {
            "experiment_id": "exp-001",
            "paper_id": "arxiv:2301.00001",
            "metric_name": "throughput",
            "baseline_value": 1000.0,
            "experiment_value": 1350.0,
            "statistical_significance": 0.95,
            "sample_size": 1000,
            "llm_judge_score": 0.85,
            "code_quality_metrics": {
                "complexity": 0.6,
                "readability": 0.8,
                "best_practices": 0.9
            }
        }

    def test_realistic_reward_calculation(self, realistic_calculator, realistic_experiment_result):
        """Test realistic reward calculation."""
        baseline = realistic_experiment_result["baseline_value"]
        experiment = realistic_experiment_result["experiment_value"]
        llm_score = realistic_experiment_result["llm_judge_score"]

        reward = realistic_calculator.calculate_with_judge(
            baseline=baseline,
            experiment=experiment,
            llm_judge_score=llm_score
        )

        assert 0 <= reward <= 1.0

    def test_reward_consistency(self, realistic_calculator):
        """Test reward calculation consistency."""
        baseline = 100.0
        experiment = 120.0

        reward1 = realistic_calculator.calculate(baseline, experiment)
        reward2 = realistic_calculator.calculate(baseline, experiment)

        assert reward1 == reward2

    def test_reward_monotonicity(self, realistic_calculator):
        """Test reward increases with improvement."""
        baseline = 100.0

        rewards = []
        for improvement in [0.10, 0.20, 0.30, 0.40, 0.50]:
            experiment = baseline * (1 + improvement)
            reward = realistic_calculator.calculate(baseline, experiment)
            rewards.append(reward)

        # Rewards should be non-decreasing
        for i in range(1, len(rewards)):
            assert rewards[i] >= rewards[i-1]


@pytest.mark.parametrize("baseline,experiment,expected_sign", [
    (100.0, 110.0, "positive"),    # Improvement
    (100.0, 90.0, "negative"),     # Degradation
    (100.0, 102.0, "zero"),        # Below threshold
    (100.0, 100.0, "zero"),        # No change
])
def test_reward_sign(baseline, experiment, expected_sign):
    """Test reward sign for different scenarios."""
    calculator = RewardCalculator(improvement_threshold=0.05)
    reward = calculator.calculate(baseline, experiment)

    if expected_sign == "positive":
        assert reward > 0
    elif expected_sign == "negative":
        assert reward < 0
    else:
        assert reward == 0
