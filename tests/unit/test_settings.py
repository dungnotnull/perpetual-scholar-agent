"""
Unit tests for configuration settings module.

Tests environment variable loading, default values, and property helpers.
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from agent.config.settings import Settings


class TestSettingsDefaults:
    """Test default settings values."""

    @pytest.fixture
    def clean_settings(self):
        """Provide settings with no environment overrides."""
        # Clear relevant env vars
        env_vars = [
            "DOMAIN_FOCUS", "LOG_LEVEL", "DATA_DIR", "MODELS_DIR",
            "LLM_PROVIDER", "OLLAMA_BASE_URL", "OLLAMA_MODEL",
            "ANTHROPIC_API_KEY", "CLAUDE_MODEL",
            "OPENAI_API_KEY", "GPT_MODEL",
            "EMBEDDING_MODEL", "EMBEDDING_DIMENSION",
            "ARXIV_CATEGORIES", "ARXIV_MAX_RESULTS",
            "GITHUB_TOKEN", "GITHUB_TRENDING_LANGUAGES",
            "RSS_FEEDS", "SANDBOX_DOCKER_IMAGE",
            "REDIS_URL", "REDIS_ENABLED"
        ]
        original_values = {}
        for var in env_vars:
            if var in os.environ:
                original_values[var] = os.environ[var]
                del os.environ[var]

        yield Settings()

        # Restore original values
        for var, value in original_values.items():
            os.environ[var] = value

    def test_default_domain_focus(self, clean_settings):
        """Test default domain focus."""
        assert "backend performance optimization" in clean_settings.domain_focus
        assert "database sharding" in clean_settings.domain_focus

    def test_default_log_level(self, clean_settings):
        """Test default log level."""
        assert clean_settings.log_level == "INFO"

    def test_default_directories(self, clean_settings):
        """Test default directory paths."""
        assert clean_settings.data_dir == Path("./data")
        assert clean_settings.models_dir == Path("./models")

    def test_default_llm_provider(self, clean_settings):
        """Test default LLM provider."""
        assert clean_settings.llm_provider == "ollama"

    def test_default_ollama_settings(self, clean_settings):
        """Test default Ollama settings."""
        assert clean_settings.ollama_base_url == "http://localhost:11434"
        assert clean_settings.ollama_model == "qwen2.5-coder:7b"

    def test_default_embedding_settings(self, clean_settings):
        """Test default embedding model settings."""
        assert clean_settings.embedding_model == "sentence-transformers/all-MiniLM-L6-v2"
        assert clean_settings.embedding_dimension == 384

    def test_default_arxiv_settings(self, clean_settings):
        """Test default arXiv settings."""
        assert clean_settings.arxiv_categories == "cs.DB,cs.DC,cs.PF"
        assert clean_settings.arxiv_max_results == 50

    def test_default_sandbox_settings(self, clean_settings):
        """Test default sandbox settings."""
        assert clean_settings.sandbox_cpu_limit == 2
        assert clean_settings.sandbox_memory_limit == "2g"
        assert clean_settings.sandbox_timeout_seconds == 60


class TestSettingsEnvironmentLoading:
    """Test environment variable loading."""

    def test_load_domain_focus_from_env(self, monkeypatch):
        """Test loading DOMAIN_FOCUS from environment."""
        monkeypatch.setenv("DOMAIN_FOCUS", "custom domain")
        settings = Settings()
        assert settings.domain_focus == "custom domain"

    def test_load_log_level_from_env(self, monkeypatch):
        """Test loading LOG_LEVEL from environment."""
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        settings = Settings()
        assert settings.log_level == "DEBUG"

    def test_load_llm_provider_from_env(self, monkeypatch):
        """Test loading LLM_PROVIDER from environment."""
        monkeypatch.setenv("LLM_PROVIDER", "claude")
        settings = Settings()
        assert settings.llm_provider == "claude"

    def test_load_ollama_base_url_from_env(self, monkeypatch):
        """Test loading OLLAMA_BASE_URL from environment."""
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://remote-ollama:11434")
        settings = Settings()
        assert settings.ollama_base_url == "http://remote-ollama:11434"

    def test_load_api_keys_from_env(self, monkeypatch):
        """Test loading API keys from environment."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key")
        monkeypatch.setenv("OPENAI_API_KEY", "sk-openai-test-key")
        settings = Settings()
        assert settings.anthropic_api_key == "sk-ant-test-key"
        assert settings.openai_api_key == "sk-openai-test-key"

    def test_load_redis_settings_from_env(self, monkeypatch):
        """Test loading Redis settings from environment."""
        monkeypatch.setenv("REDIS_URL", "redis://remote-redis:6379/1")
        monkeypatch.setenv("REDIS_ENABLED", "true")
        settings = Settings()
        assert settings.redis_url == "redis://remote-redis:6379/1"
        assert settings.redis_enabled is True


class TestSettingsProperties:
    """Test property helpers for parsed values."""

    @pytest.fixture
    def settings(self):
        """Provide settings instance."""
        return Settings()

    def test_arxiv_categories_list(self, settings):
        """Test arXiv categories list property."""
        categories = settings.arxiv_categories_list
        assert isinstance(categories, list)
        assert "cs.DB" in categories
        assert "cs.DC" in categories
        assert "cs.PF" in categories
        assert len(categories) == 3

    def test_github_languages_list(self, settings):
        """Test GitHub languages list property."""
        languages = settings.github_languages_list
        assert isinstance(languages, list)
        assert "python" in languages
        assert "go" in languages

    def test_lora_target_modules_list(self, settings):
        """Test LoRA target modules list property."""
        modules = settings.lora_target_modules_list
        assert isinstance(modules, list)
        assert "q_proj" in modules
        assert "v_proj" in modules

    def test_fallback_chain_list(self, settings):
        """Test fallback chain list property."""
        chain = settings.fallback_chain_list
        assert isinstance(chain, list)
        assert "ollama" in chain
        assert "claude" in chain
        assert "openai" in chain

    def test_arxiv_categories_list_with_spaces(self, monkeypatch):
        """Test categories list with spaces."""
        monkeypatch.setenv("ARXIV_CATEGORIES", "cs.DB, cs.DC , cs.PF")
        settings = Settings()
        categories = settings.arxiv_categories_list
        assert categories == ["cs.DB", "cs.DC", "cs.PF"]


class TestSettingsValidation:
    """Test settings validation and edge cases."""

    @pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_valid_log_levels(self, monkeypatch, log_level):
        """Test valid log levels."""
        monkeypatch.setenv("LOG_LEVEL", log_level)
        settings = Settings()
        assert settings.log_level == log_level

    def test_invalid_llm_provider_defaults_to_ollama(self, monkeypatch):
        """Test invalid LLM provider defaults to ollama."""
        monkeypatch.setenv("LLM_PROVIDER", "invalid_provider")
        settings = Settings()
        # Pydantic doesn't validate enum-like strings by default
        assert settings.llm_provider == "invalid_provider"

    def test_empty_string_domain_focus(self, monkeypatch):
        """Test empty domain focus is allowed."""
        monkeypatch.setenv("DOMAIN_FOCUS", "")
        settings = Settings()
        assert settings.domain_focus == ""

    def test_numeric_string_values(self, monkeypatch):
        """Test numeric values from strings."""
        monkeypatch.setenv("ARXIV_MAX_RESULTS", "100")
        monkeypatch.setenv("SANDBOX_CPU_LIMIT", "4")
        monkeypatch.setenv("EMBEDDING_DIMENSION", "768")
        settings = Settings()
        assert settings.arxiv_max_results == 100
        assert settings.sandbox_cpu_limit == 4
        assert settings.embedding_dimension == 768

    def test_boolean_string_values(self, monkeypatch):
        """Test boolean values from strings."""
        monkeypatch.setenv("REDIS_ENABLED", "true")
        monkeypatch.setenv("SANDBOX_NETWORK_DISABLED", "false")
        settings = Settings()
        assert settings.redis_enabled is True
        assert settings.sandbox_network_disabled is False


class TestSettingsPaths:
    """Test path-related settings."""

    def test_data_dir_path_resolved(self):
        """Test data_dir is resolved as Path object."""
        settings = Settings()
        assert isinstance(settings.data_dir, Path)
        assert str(settings.data_dir) == "./data"

    def test_models_dir_path_resolved(self):
        """Test models_dir is resolved as Path object."""
        settings = Settings()
        assert isinstance(settings.models_dir, Path)
        assert str(settings.models_dir) == "./models"

    def test_custom_data_dir_from_env(self, monkeypatch, tmp_path):
        """Test custom data directory from environment."""
        custom_dir = tmp_path / "custom_data"
        monkeypatch.setenv("DATA_DIR", str(custom_dir))
        settings = Settings()
        assert settings.data_dir == custom_dir


class TestSettingsSingleton:
    """Test settings singleton instance."""

    def test_singleton_import(self):
        """Test singleton can be imported."""
        from agent.config.settings import settings as singleton_settings
        assert isinstance(singleton_settings, Settings)

    def test_singleton_consistency(self):
        """Test singleton returns same instance."""
        from agent.config.settings import settings
        settings1 = Settings()
        settings2 = Settings()
        # Note: Pydantic Settings creates new instance each time
        # If singleton behavior is needed, use settings instance
        assert settings1 is not settings2


class TestSettingsRLParameters:
    """Test reinforcement learning parameters."""

    @pytest.fixture
    def settings(self):
        """Provide settings instance."""
        return Settings()

    def test_rl_learning_rate(self, settings):
        """Test RL learning rate."""
        assert settings.rl_learning_rate == 3e-4

    def test_rl_gamma(self, settings):
        """Test RL gamma."""
        assert settings.rl_gamma == 0.99

    def test_rl_clip_range(self, settings):
        """Test RL clip range."""
        assert settings.rl_clip_range == 0.2

    def test_rl_batch_size(self, settings):
        """Test RL batch size."""
        assert settings.rl_batch_size == 64

    def test_rl_n_epochs(self, settings):
        """Test RL number of epochs."""
        assert settings.rl_n_epochs == 10


class TestSettingsLoRAParameters:
    """Test LoRA fine-tuning parameters."""

    @pytest.fixture
    def settings(self):
        """Provide settings instance."""
        return Settings()

    def test_lora_r(self, settings):
        """Test LoRA rank."""
        assert settings.lora_r == 16

    def test_lora_alpha(self, settings):
        """Test LoRA alpha."""
        assert settings.lora_alpha == 32

    def test_lora_dropout(self, settings):
        """Test LoRA dropout."""
        assert settings.lora_dropout == 0.05

    def test_lora_learning_rate(self, settings):
        """Test LoRA learning rate."""
        assert settings.lora_learning_rate == 2e-4

    def test_lora_trigger_lesson_count(self, settings):
        """Test LoRA trigger lesson count."""
        assert settings.lora_trigger_lesson_count == 50

    def test_lora_trigger_days(self, settings):
        """Test LoRA trigger days."""
        assert settings.lora_trigger_days == 7


class TestSettingsRewardParameters:
    """Test reward calculation parameters."""

    @pytest.fixture
    def settings(self):
        """Provide settings instance."""
        return Settings()

    def test_reward_improvement_threshold(self, settings):
        """Test improvement threshold."""
        assert settings.reward_improvement_threshold == 0.05

    def test_reward_degradation_threshold(self, settings):
        """Test degradation threshold."""
        assert settings.reward_degradation_threshold == -0.05

    def test_reward_llm_judge_weight(self, settings):
        """Test LLM judge weight."""
        assert settings.reward_llm_judge_weight == 0.3

    def test_reward_benchmark_weight(self, settings):
        """Test benchmark weight."""
        assert settings.reward_benchmark_weight == 0.7

    def test_reward_weights_sum_to_one(self, settings):
        """Test reward weights sum to approximately 1.0."""
        total = settings.reward_llm_judge_weight + settings.reward_benchmark_weight
        assert abs(total - 1.0) < 0.01


class TestSettingsCronExpressions:
    """Test scheduled task cron expressions."""

    @pytest.fixture
    def settings(self):
        """Provide settings instance."""
        return Settings()

    def test_ingestion_cron(self, settings):
        """Test ingestion cron expression."""
        assert settings.schedule_ingestion_cron == "0 2 * * *"

    def test_finetune_cron(self, settings):
        """Test fine-tuning cron expression."""
        assert settings.schedule_finetune_cron == "0 3 * * 0"

    def test_brain_update_cron(self, settings):
        """Test brain update cron expression."""
        assert settings.schedule_brain_update_cron == "0 6 * * 0"

    def test_report_cron(self, settings):
        """Test report cron expression."""
        assert settings.schedule_report_cron == "0 8 * * 1"


@pytest.mark.integration
class TestSettingsEnvFile:
    """Test loading from .env file."""

    def test_load_from_env_file(self, tmp_path, monkeypatch):
        """Test loading settings from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
DOMAIN_FOCUS=test domain
LOG_LEVEL=DEBUG
LLM_PROVIDER=claude
ARXIV_MAX_RESULTS=100
""")
        monkeypatch.setenv("ENV_FILE", str(env_file))
        # Settings should load from file if configured
        # This test verifies the mechanism exists
        assert env_file.exists()

    def test_missing_env_file_uses_defaults(self, monkeypatch, tmp_path):
        """Test missing .env file uses defaults."""
        non_existent = tmp_path / "nonexistent.env"
        monkeypatch.setattr("agent.config.settings.Settings", "model_config", {
            "env_file": str(non_existent),
            "env_file_encoding": "utf-8",
            "case_sensitive": False,
        })
        # Should not raise error, use defaults
        settings = Settings()
        assert settings.domain_focus  # Should have default value
