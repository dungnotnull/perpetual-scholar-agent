"""Finetune: Ollama model reloader after LoRA adapter update."""
from __future__ import annotations

import logging
from pathlib import Path

import httpx

from agent.config.settings import settings

logger = logging.getLogger(__name__)


def reload_ollama_model(adapter_path: str | None = None) -> bool:
    """Reload the Ollama model with a new LoRA adapter.

    This calls the Ollama API to create a new model that combines
    the base model with the LoRA adapter.

    Args:
        adapter_path: Path to the LoRA adapter directory. Defaults to latest.

    Returns:
        True if reload was successful.
    """
    if adapter_path is None:
        # Find latest adapter
        adapter_dirs = sorted(Path(settings.models_dir).glob("lora_adapter_v*"))
        if not adapter_dirs:
            logger.warning("No LoRA adapter found — cannot reload")
            return False
        adapter_path = str(adapter_dirs[-1])

    base_model = settings.ollama_model
    new_model_name = f"{base_model}-finetuned"

    logger.info(f"Reloading Ollama model: {base_model} + adapter at {adapter_path}")

    url = f"{settings.ollama_base_url.rstrip('/')}/api/create"

    # Ollama create API with adapter
    payload = {
        "name": new_model_name,
        "from": base_model,
        "adapter": adapter_path,
    }

    try:
        resp = httpx.post(url, json=payload, timeout=300.0)
        resp.raise_for_status()
        logger.info(f"Successfully reloaded model as '{new_model_name}'")

        # Update settings to use the finetuned model
        settings.ollama_model = new_model_name
        return True

    except httpx.HTTPStatusError as e:
        logger.error(f"Failed to reload Ollama model: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error reloading Ollama: {e}")
        return False
