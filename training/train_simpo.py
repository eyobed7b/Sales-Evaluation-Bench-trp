"""
Tenacious-Bench v0.1 — Preference Judge Training Script
Trains Qwen 0.5B + LoRA as a compliance critic via CPO (reference-free).

CPO (Contrastive Preference Optimization) is used because it is available in
stable TRL releases. Like SimPO, CPO is reference-free — it does not require
a frozen reference model copy in VRAM, making it feasible on Colab T4.

Run on Google Colab T4:
    !pip install unsloth trl peft datasets accelerate
    !python training/train_simpo.py

Outputs:
    training/runs/simpo_judge_v1/  — LoRA adapter weights
    training/loss_log.json         — per-step training loss
"""

import json
import os
from pathlib import Path

try:
    from unsloth import FastLanguageModel
    from trl import CPOTrainer, CPOConfig
    from datasets import Dataset
    import torch
    HAVE_DEPS = True
except ImportError:
    Dataset = None  # type: ignore
    HAVE_DEPS = False
    print("Dependencies not installed — training cannot run. Install via:")
    print("  pip install unsloth trl peft datasets accelerate")

# ── Config ───────────────────────────────────────────────────────────────────

MODEL_NAME   = "Qwen/Qwen3-0.5B-Instruct"
OUTPUT_DIR   = "training/runs/simpo_judge_v1"
DATA_PATH    = "training_data/simpo_pairs.jsonl"
LOG_PATH     = "training/loss_log.json"
MAX_SEQ_LEN  = 1024
LORA_R       = 16
LORA_ALPHA   = 32
LORA_DROPOUT = 0.05
CPO_BETA     = 2.0
LR           = 1e-5
BATCH_SIZE   = 2
GRAD_ACCUM   = 4
EPOCHS       = 3
WARMUP_STEPS = 10


def load_pairs(path: str) -> "Dataset":
    records = [json.loads(l) for l in open(path)]
    return Dataset.from_list([
        {"prompt": r["prompt"], "chosen": r["chosen"], "rejected": r["rejected"]}
        for r in records
    ])


def train():
    if not HAVE_DEPS:
        raise RuntimeError("Dependencies not installed")

    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LEN,
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    dataset = load_pairs(DATA_PATH)

    config = CPOConfig(
        output_dir=OUTPUT_DIR,
        beta=CPO_BETA,
        learning_rate=LR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        num_train_epochs=EPOCHS,
        warmup_steps=WARMUP_STEPS,
        max_length=MAX_SEQ_LEN,
        logging_steps=5,
        save_steps=50,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        report_to="none",
    )

    trainer = CPOTrainer(
        model=model,
        args=config,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )

    result = trainer.train()

    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)

    log = [
        {"step": int(e["step"]), "loss": round(float(e["loss"]), 4)}
        for e in trainer.state.log_history
        if "loss" in e
    ]
    json.dump(log, open(LOG_PATH, "w"), indent=2)
    print(f"Training complete. Adapter → {OUTPUT_DIR}")
    print(f"Loss log → {LOG_PATH}")
    return result


if __name__ == "__main__":
    if not HAVE_DEPS:
        print("Run this script on Google Colab T4 after installing dependencies.")
        raise SystemExit(1)
    train()
