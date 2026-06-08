"""perpetual-scholar-agent — central configuration via Pydantic Settings."""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """All environment-driven configuration. Values are loaded from .env or env vars."""

    # ── General ────────────────────────────────────────────────────────────
    domain_focus: str = "backend performance optimization: database sharding, caching strategies, async I/O patterns, clean architecture"
    log_level: str = "INFO"
    data_dir: Path = Path("./data")
    models_dir: Path = Path("./models")

    # ── LLM Provider ───────────────────────────────────────────────────────
    llm_provider: str = "ollama"  # ollama | claude | openai
    llm_fallback_chain: str = "ollama,claude,openai"

    # ── Ollama (local SLM) ─────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:7b"

    # ── Anthropic Claude API ────────────────────────────────────────────────
    anthropic_api_key: Optional[str] = None
    claude_model: str = "claude-sonnet-4-6"

    # ── OpenAI GPT API ──────────────────────────────────────────────────────
    openai_api_key: Optional[str] = None
    gpt_model: str = "gpt-4o"

    # ── Embeddings ──────────────────────────────────────────────────────────
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dimension: int = 384

    # ── arXiv ────────────────────────────────────────────────────────────────
    arxiv_categories: str = "cs.DB,cs.DC,cs.PF"
    arxiv_max_results: int = 50

    # ── GitHub ──────────────────────────────────────────────────────────────
    github_token: Optional[str] = None
    github_trending_languages: str = "python,go"
    github_trending_since: str = "daily"

    # ── RSS Feeds ────────────────────────────────────────────────────────────
    rss_feeds: str = "https://medium.com/feed/engineering,https://hnrss.org/frontpage"

    # ── Docker Sandbox ──────────────────────────────────────────────────────
    sandbox_docker_image: str = "psa-sandbox:latest"
    sandbox_cpu_limit: int = 2
    sandbox_memory_limit: str = "2g"
    sandbox_timeout_seconds: int = 60
    sandbox_network_disabled: bool = True

    # ── Benchmark ──────────────────────────────────────────────────────────
    benchmark_warmup_iterations: int = 5
    benchmark_measure_iterations: int = 30
    benchmark_timeout_seconds: int = 30

    # ── RL / PPO ────────────────────────────────────────────────────────────
    rl_learning_rate: float = 3e-4
    rl_gamma: float = 0.99
    rl_clip_range: float = 0.2
    rl_n_steps: int = 128
    rl_batch_size: int = 64
    rl_n_epochs: int = 10

    # ── LoRA Fine-tuning ────────────────────────────────────────────────────
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    lora_target_modules: str = "q_proj,v_proj"
    lora_training_epochs: int = 3
    lora_learning_rate: float = 2e-4
    lora_trigger_lesson_count: int = 50
    lora_trigger_days: int = 7
    lora_max_seq_length: int = 2048

    # ── Scheduler ───────────────────────────────────────────────────────────
    schedule_ingestion_cron: str = "0 2 * * *"
    schedule_finetune_cron: str = "0 3 * * 0"
    schedule_brain_update_cron: str = "0 6 * * 0"
    schedule_report_cron: str = "0 8 * * 1"

    # ── Reward ──────────────────────────────────────────────────────────────
    reward_improvement_threshold: float = 0.05
    reward_degradation_threshold: float = -0.05
    reward_llm_judge_weight: float = 0.3
    reward_benchmark_weight: float = 0.7

    # ── Monitoring ──────────────────────────────────────────────────────────
    prometheus_port: int = 9090
    fastapi_dashboard_host: str = "0.0.0.0"
    fastapi_dashboard_port: int = 8080

    # ── Redis (optional) ────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False

    # ── Derived helpers ─────────────────────────────────────────────────────
    @property
    def arxiv_categories_list(self) -> List[str]:
        return [c.strip() for c in self.arxiv_categories.split(",")]

    @property
    def github_languages_list(self) -> List[str]:
        return [l.strip() for l in self.github_trending_languages.split(",")]

    @property
    def lora_target_modules_list(self) -> List[str]:
        return [m.strip() for m in self.lora_target_modules.split(",")]

    @property
    def fallback_chain_list(self) -> List[str]:
        return [p.strip() for p in self.llm_fallback_chain.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton settings instance — import from anywhere:
#   from agent.config.settings import settings
settings = Settings()
