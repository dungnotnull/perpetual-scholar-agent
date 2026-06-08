"""Finetune: LoRA fine-tuning pipeline using Hugging Face PEFT + trl.

This module handles the complete fine-tuning workflow:
1. Export verified lessons as JSONL training data
2. Configure LoRA adapters (r=16, alpha=32)
3. Run SFTTrainer with QLoRA for memory efficiency
4. Save versioned adapter and update latest symlink
5. Reload Ollama model with the new adapter
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from agent.config.settings import settings
from agent.finetune.adapter_manager import save_adapter_version

logger = logging.getLogger(__name__)


def run_lora_finetuning(
    dataset_path: Optional[str] = None,
    output_dir: Optional[str] = None,
    num_epochs: Optional[int] = None,
    learning_rate: Optional[float] = None,
    max_seq_length: Optional[int] = None,
) -> str:
    """Run LoRA fine-tuning on the local SLM with verified lessons.

    Args:
        dataset_path: Path to JSONL training dataset.
        output_dir: Directory to save the LoRA adapter.
        num_epochs: Number of training epochs.
        learning_rate: Learning rate for training.
        max_seq_length: Maximum sequence length.

    Returns:
        Path to the saved adapter directory.
    """
    from datasets import load_dataset
    from peft import LoraConfig, TaskType
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, BitsAndBytesConfig
    import torch

    dataset_path = dataset_path or str(settings.data_dir / "finetune_dataset.jsonl")
    output_dir = output_dir or str(settings.models_dir / "lora_adapter_latest")
    num_epochs = num_epochs or settings.lora_training_epochs
    learning_rate = learning_rate or settings.lora_learning_rate
    max_seq_length = max_seq_length or settings.lora_max_seq_length

    logger.info("lora_finetuning_starting", extra={
        "dataset": dataset_path,
        "output": output_dir,
        "epochs": num_epochs,
        "lr": learning_rate,
    })

    # Map Ollama model names to HuggingFace model IDs
    hf_model_map = {
        "qwen2.5-coder:7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "qwen2.5-coder-7b": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "deepseek-coder:6.7b": "deepseek-ai/deepseek-coder-6.7b-instruct",
        "deepseek-coder-7b": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
    }
    model_key = settings.ollama_model.replace("-", "-")
    hf_model_id = hf_model_map.get(settings.ollama_model, "Qwen/Qwen2.5-Coder-7B-Instruct")

    logger.info("lora_loading_base_model", extra={"model": hf_model_id})

    # Configure 4-bit quantization for memory efficiency (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # Load base model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained(hf_model_id)
    tokenizer.pad_token = tokenizer.pad_token or tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        hf_model_id,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    # Configure LoRA
    lora_config = LoraConfig(
        r=settings.lora_r,
        lora_alpha=settings.lora_alpha,
        lora_dropout=settings.lora_dropout,
        target_modules=settings.lora_target_modules_list,
        bias="none",
        task_type=TaskType.CAUSAL_LM,
    )

    # Load dataset
    dataset = load_dataset("json", data_files=dataset_path, split="train")
    logger.info("lora_dataset_loaded", extra={"size": len(dataset)})

    # Format dataset for SFT
    def format_example(example):
        return {
            "text": f"### Instruction:\n{example['prompt']}\n\n### Response:\n{example['completion']}"
        }

    dataset = dataset.map(format_example)

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=learning_rate,
        fp16=True,
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="no",
        max_grad_norm=1.0,
        warmup_ratio=0.1,
        report_to=["tensorboard"],
        remove_unused_columns=False,
        save_total_limit=2,
        dataloader_pin_memory=False,
    )

    # Create trainer
    from trl import SFTTrainer

    trainer = SFTTrainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        peft_config=lora_config,
        max_seq_length=max_seq_length,
        formatting_func=lambda x: x["text"],
    )

    # Train
    logger.info("lora_training_started")
    train_result = trainer.train()

    # Save adapter
    trainer.save_model(output_dir)
    logger.info("lora_adapter_saved", extra={"path": output_dir})

    # Save versioned copy and update symlink
    version = save_adapter_version(output_dir)

    # Record training metrics
    train_loss = train_result.training_loss
    logger.info("lora_training_complete", extra={
        "version": version,
        "train_loss": train_loss,
        "epochs": num_epochs,
    })

    # Update database
    _record_training_in_db(version, len(dataset), train_loss, output_dir)

    return output_dir


def _record_training_in_db(version: str, num_examples: int, train_loss: float, adapter_path: str) -> None:
    """Record the training run in the database."""
    import sqlite3

    db_path = str(settings.data_dir / "psa.db")
    try:
        conn = sqlite3.connect(db_path)
        conn.execute(
            """INSERT INTO finetune_runs
               (adapter_version, num_lessons_used, train_loss, adapter_path)
               VALUES (?, ?, ?, ?)""",
            (version, num_examples, train_loss, adapter_path),
        )
        conn.execute("UPDATE lessons SET is_used_in_lora = 1 WHERE is_used_in_lora = 0")
        conn.commit()
        conn.close()
        logger.info("finetune_recorded_in_db", extra={"version": version, "num_examples": num_examples})
    except Exception as e:
        logger.warning("finetune_db_record_failed", extra={"error": str(e)})
