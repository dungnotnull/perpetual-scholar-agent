"""RL environment: OpenAI Gym-compatible environment wrapping the scholar pipeline."""
from __future__ import annotations

import logging
from typing import Dict, Optional, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from agent.config.settings import settings

logger = logging.getLogger(__name__)

# Action constants
FETCH_PAPER = 0
GENERATE_CODE = 1
RUN_BENCHMARK = 2
STORE_LESSON = 3
SKIP = 4

ACTION_NAMES = {
    FETCH_PAPER: "FETCH_PAPER",
    GENERATE_CODE: "GENERATE_CODE",
    RUN_BENCHMARK: "RUN_BENCHMARK",
    STORE_LESSON: "STORE_LESSON",
    SKIP: "SKIP",
}


class ScholarEnv(gym.Env):
    """Reinforcement learning environment for the perpetual-scholar-agent.

    State space (observation):
        - paper_embedding: 384-dim (all-MiniLM-L6-v2 embedding of current paper)
        - baseline_score: 1-dim (current baseline ops/sec, normalized)
        - sandbox_available: 1-dim (1 if sandbox is free, 0 if busy)
        - queue_depth: 1-dim (number of papers in processing queue, normalized)
        Total: 387-dim Box space

    Action space:
        Discrete(5) = {FETCH_PAPER, GENERATE_CODE, RUN_BENCHMARK, STORE_LESSON, SKIP}

    Reward:
        Combined benchmark + LLM judge reward, clamped to [-1, +1].
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        embedding_dim: int = 384,
        max_queue_depth: int = 50,
    ):
        super().__init__()

        self.embedding_dim = embedding_dim
        self.max_queue_depth = max_queue_depth

        # Observation: (paper_embedding[384], baseline_score[1], sandbox_available[1], queue_depth[1])
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.embedding_dim + 3,),
            dtype=np.float32,
        )

        # Action: discrete 5 actions
        self.action_space = spaces.Discrete(5)

        # Internal state
        self.current_paper_embedding = np.zeros(self.embedding_dim, dtype=np.float32)
        self.baseline_score = 1.0  # Normalized baseline (1.0 = baseline)
        self.sandbox_available = 1.0
        self.queue_depth = 0
        self.current_paper_info: Optional[Dict] = None
        self.current_code: Optional[str] = None
        self.current_benchmark_result: Optional[Dict] = None
        self.episode_reward = 0.0
        self.step_count = 0
        self.max_steps = 100

    def _get_obs(self) -> np.ndarray:
        """Build the observation vector."""
        obs = np.concatenate([
            self.current_paper_embedding,
            np.array([self.baseline_score], dtype=np.float32),
            np.array([self.sandbox_available], dtype=np.float32),
            np.array([self.queue_depth / self.max_queue_depth], dtype=np.float32),
        ])
        return obs

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None,
    ) -> Tuple[np.ndarray, Dict]:
        """Reset the environment to start a new episode."""
        super().reset(seed=seed)

        self.current_paper_embedding = np.zeros(self.embedding_dim, dtype=np.float32)
        self.baseline_score = 1.0
        self.sandbox_available = 1.0
        self.queue_depth = 0
        self.current_paper_info = None
        self.current_code = None
        self.current_benchmark_result = None
        self.episode_reward = 0.0
        self.step_count = 0

        return self._get_obs(), {}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute one step in the environment.

        Args:
            action: Integer action (0-4).

        Returns:
            (observation, reward, terminated, truncated, info)
        """
        self.step_count += 1
        reward = 0.0
        info = {"action": ACTION_NAMES.get(action, "UNKNOWN")}

        if action == FETCH_PAPER:
            # Load next paper from queue
            reward = self._action_fetch_paper()
        elif action == GENERATE_CODE:
            # Generate benchmark code for current paper
            reward = self._action_generate_code()
        elif action == RUN_BENCHMARK:
            # Execute code in sandbox
            reward = self._action_run_benchmark()
        elif action == STORE_LESSON:
            # Store verified lesson if benchmark was positive
            reward = self._action_store_lesson()
        elif action == SKIP:
            # Skip current paper
            reward = -0.01  # Small negative reward for skipping
            self.current_paper_info = None
            self.current_code = None
            self.current_benchmark_result = None
        else:
            reward = -0.1  # Penalty for invalid action

        self.episode_reward += reward

        # Episode termination conditions
        terminated = False
        truncated = self.step_count >= self.max_steps

        return self._get_obs(), reward, terminated, truncated, info

    def _action_fetch_paper(self) -> float:
        """Simulate fetching next paper from queue."""
        # In real implementation, this loads from the ingestion pipeline
        self.current_paper_embedding = np.random.randn(self.embedding_dim).astype(np.float32)
        self.current_paper_info = {"source": "simulated", "title": "Simulated Paper"}
        self.queue_depth = max(0, self.queue_depth - 1)
        return -0.01  # Small cost for fetching

    def _action_generate_code(self) -> float:
        """Simulate generating benchmark code."""
        if self.current_paper_info is None:
            return -0.05  # Penalty: no paper to generate code for
        self.current_code = "# Simulated benchmark code"
        return -0.02  # Small cost for generation

    def _action_run_benchmark(self) -> float:
        """Simulate running benchmark in sandbox."""
        if self.current_code is None:
            return -0.05  # Penalty: no code to run
        self.current_benchmark_result = {
            "ops_per_sec": 1.0 + np.random.randn() * 0.1,
            "baseline_ops_per_sec": 1.0,
        }
        self.sandbox_available = 0.0  # Sandbox busy
        return -0.01  # Small cost for execution

    def _action_store_lesson(self) -> float:
        """Simulate storing a lesson."""
        if self.current_benchmark_result is None:
            return -0.05  # Penalty: no benchmark to store

        from agent.reward.calculator import calculate_benchmark_reward
        new_metric = self.current_benchmark_result.get("ops_per_sec", 1.0)
        baseline = self.current_benchmark_result.get("baseline_ops_per_sec", 1.0)
        reward = calculate_benchmark_reward(new_metric, baseline)

        # Reset state for next paper
        self.current_paper_info = None
        self.current_code = None
        self.current_benchmark_result = None
        self.sandbox_available = 1.0

        return reward
