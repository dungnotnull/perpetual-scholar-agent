"""RL: PPO policy for paper/action selection with full training loop."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback, EvalCallback
from stable_baselines3.common.vec_env import DummyVecEnv

from agent.config.settings import settings
from agent.rl.environment import ScholarEnv

logger = logging.getLogger(__name__)


class RewardLoggingCallback(BaseCallback):
    """Custom callback to log episode rewards during training.

    Logs average reward every ``log_freq`` episodes to both Python logger
    and TensorBoard.
    """

    def __init__(self, log_freq: int = 100, verbose: int = 0):
        super().__init__(verbose)
        self.log_freq = log_freq
        self.episode_rewards = []
        self.current_episode_reward = 0.0
        self.episode_count = 0

    def _on_step(self) -> bool:
        # Accumulate rewards for the current episode
        if len(self.locals.get("rewards", [])) > 0:
            self.current_episode_reward += self.locals["rewards"][0]

        # Check if episode ended
        dones = self.locals.get("dones", [False])
        if dones[0]:
            self.episode_rewards.append(self.current_episode_reward)
            self.current_episode_reward = 0.0
            self.episode_count += 1

            if self.episode_count % self.log_freq == 0:
                recent = self.episode_rewards[-self.log_freq:]
                avg = sum(recent) / len(recent)
                logger.info(
                    "rl_training_progress",
                    extra={
                        "episode": self.episode_count,
                        "avg_reward": round(avg, 4),
                        "episodes_logged": len(self.episode_rewards),
                    },
                )
                # Log to TensorBoard
                self.logger.record("rl/avg_reward", avg)
                self.logger.record("rl/episode_count", self.episode_count)

        return True


def create_ppo_policy(
    env: Optional[ScholarEnv] = None,
    policy_kwargs: Optional[dict] = None,
    learning_rate: Optional[float] = None,
    n_steps: Optional[int] = None,
    batch_size: Optional[int] = None,
    n_epochs: Optional[int] = None,
) -> PPO:
    """Create a PPO policy with configured hyperparameters.

    Args:
        env: Gym environment. Creates default ScholarEnv if None.
        policy_kwargs: Override policy network architecture.
        learning_rate: Learning rate override.
        n_steps: Steps per rollout override.
        batch_size: Minibatch size override.
        n_epochs: Optimization epochs override.

    Returns:
        Configured PPO model ready for training.
    """
    if env is None:
        env = ScholarEnv()

    vec_env = DummyVecEnv([lambda: env])

    default_policy_kwargs = dict(
        net_arch=[256, 128, 64],
    )

    tensorboard_dir = settings.models_dir / "tensorboard"
    tensorboard_dir.mkdir(parents=True, exist_ok=True)

    model = PPO(
        policy="MlpPolicy",
        env=vec_env,
        learning_rate=learning_rate or settings.rl_learning_rate,
        n_steps=n_steps or settings.rl_n_steps,
        batch_size=batch_size or settings.rl_batch_size,
        n_epochs=n_epochs or settings.rl_n_epochs,
        gamma=settings.rl_gamma,
        clip_range=settings.rl_clip_range,
        policy_kwargs=policy_kwargs or default_policy_kwargs,
        verbose=1,
        tensorboard_log=str(tensorboard_dir),
    )

    logger.info("ppo_policy_created", extra={
        "learning_rate": model.learning_rate,
        "n_steps": model.n_steps,
        "batch_size": model.batch_size,
        "n_epochs": model.n_epochs,
        "gamma": model.gamma,
    })

    return model


def train_policy(
    total_timesteps: int = 10_000,
    save_path: Optional[str] = None,
    eval_env: Optional[ScholarEnv] = None,
) -> PPO:
    """Train the PPO policy on the scholar environment.

    Args:
        total_timesteps: Total timesteps for training.
        save_path: Path to save the trained model.
        eval_env: Optional separate environment for evaluation.

    Returns:
        Trained PPO model.
    """
    env = ScholarEnv()
    model = create_ppo_policy(env)

    if save_path is None:
        save_path = str(settings.models_dir / "rl_policy" / "ppo_scholar_latest")

    callbacks = [RewardLoggingCallback(log_freq=100)]

    # Add evaluation callback if eval environment provided
    if eval_env is not None:
        eval_vec_env = DummyVecEnv([lambda: eval_env])
        eval_callback = EvalCallback(
            eval_vec_env,
            best_model_save_path=str(settings.models_dir / "rl_policy" / "best"),
            log_path=str(settings.models_dir / "rl_policy" / "eval_logs"),
            eval_freq=500,
            n_eval_episodes=5,
            deterministic=True,
        )
        callbacks.append(eval_callback)

    logger.info("rl_training_starting", extra={"total_timesteps": total_timesteps})

    model.learn(
        total_timesteps=total_timesteps,
        callback=callbacks,
        progress_bar=True,
    )

    # Save final model
    model_path = Path(save_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(model_path))
    logger.info("rl_policy_saved", extra={"path": str(model_path)})

    # Record checkpoint in database
    _record_checkpoint(model_path, total_timesteps)

    return model


def load_policy(path: str) -> PPO:
    """Load a saved PPO policy from disk.

    Args:
        path: Path to the saved model file (.zip).

    Returns:
        Loaded PPO model.
    """
    model = PPO.load(path)
    logger.info("rl_policy_loaded", extra={"path": path})
    return model


def _record_checkpoint(model_path: Path, timesteps: int) -> None:
    """Record a policy checkpoint in the database."""
    import sqlite3

    db_path = str(settings.data_dir / "psa.db")
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            """INSERT INTO rl_policy_checkpoints (episode, avg_reward, checkpoint_path)
               VALUES (?, ?, ?)""",
            (timesteps // 128, 0.0, str(model_path)),  # episode = timesteps / n_steps
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning("rl_checkpoint_record_failed", extra={"error": str(e)})
