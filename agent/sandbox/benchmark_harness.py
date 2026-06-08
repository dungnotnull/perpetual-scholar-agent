"""Sandbox execution: benchmark result parser."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Parsed benchmark result from pytest-benchmark JSON output."""
    name: str
    ops_per_sec: float
    latency_p50_us: float    # microseconds
    latency_p99_us: float    # microseconds
    mean_us: float
    stddev_us: float
    rounds: int
    iterations: int


def parse_benchmark_json(json_data: Dict[str, Any]) -> List[BenchmarkResult]:
    """Parse pytest-benchmark JSON output into structured results.

    Args:
        json_data: Parsed JSON dict from pytest-benchmark --benchmark-json output.

    Returns:
        List of BenchmarkResult objects, one per benchmark.
    """
    results = []

    benchmarks = json_data.get("benchmarks", [])
    for bm in benchmarks:
        name = bm.get("name", "unknown")
        stats = bm.get("stats", {})

        ops_per_sec = stats.get("ops", 0.0)  # iterations per second
        mean = stats.get("mean", 0.0) * 1e6    # seconds → microseconds
        stddev = stats.get("stddev", 0.0) * 1e6
        median = stats.get("median", 0.0) * 1e6

        # pytest-benchmark doesn't directly give p99, approximate from max
        # or use the 'max' stat if available
        max_latency = stats.get("max", 0.0) * 1e6  # seconds → microseconds

        rounds = stats.get("rounds", 0)
        iterations = stats.get("iterations", 1)

        results.append(BenchmarkResult(
            name=name,
            ops_per_sec=ops_per_sec,
            latency_p50_us=median,
            latency_p99_us=max_latency,  # approximate p99 with max
            mean_us=mean,
            stddev_us=stddev,
            rounds=rounds,
            iterations=iterations,
        ))

    logger.info(f"Parsed {len(results)} benchmark results from JSON")
    return results


def extract_metrics(
    benchmark_results: List[BenchmarkResult],
    baseline_prefix: str = "baseline",
    technique_prefix: str = "technique",
) -> Dict[str, Any]:
    """Extract comparison metrics between baseline and technique benchmarks.

    Args:
        benchmark_results: List of parsed benchmark results.
        baseline_prefix: Name prefix for baseline benchmarks.
        technique_prefix: Name prefix for technique benchmarks.

    Returns:
        Dict with baseline and technique metrics plus improvement calculation.
    """
    baseline = None
    technique = None

    for result in benchmark_results:
        if baseline_prefix in result.name.lower():
            baseline = result
        elif technique_prefix in result.name.lower():
            technique = result

    if baseline is None or technique is None:
        logger.warning(
            f"Could not find baseline/technique pair. "
            f"Names: {[r.name for r in benchmark_results]}"
        )
        return {
            "baseline_found": baseline is not None,
            "technique_found": technique is not None,
            "ops_per_sec": technique.ops_per_sec if technique else 0,
            "baseline_ops_per_sec": baseline.ops_per_sec if baseline else 0,
        }

    improvement_pct = (
        (technique.ops_per_sec - baseline.ops_per_sec) / baseline.ops_per_sec * 100
        if baseline.ops_per_sec > 0 else 0.0
    )

    return {
        "baseline_found": True,
        "technique_found": True,
        "ops_per_sec": technique.ops_per_sec,
        "baseline_ops_per_sec": baseline.ops_per_sec,
        "improvement_pct": improvement_pct,
        "latency_p50_us": technique.latency_p50_us,
        "latency_p99_us": technique.latency_p99_us,
        "baseline_latency_p50_us": baseline.latency_p50_us,
        "baseline_latency_p99_us": baseline.latency_p99_us,
    }
