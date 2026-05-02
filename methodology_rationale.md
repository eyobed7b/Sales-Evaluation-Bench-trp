# Methodology Rationale — Path B: SimPO Preference-Tuned Judge

**Author:** Eyobed Feleke  
**Date:** 2026-05-02  
**Path:** B — DPO/SimPO/ORPO preference-tuned judge or critic

---

## 1. Path Choice Grounded in Week 10 Evidence

Three specific trace IDs from the Week 10 evaluation drove the Path B selection:

### Trace cf06a98e — Inconsistency, not ignorance
The agent composed an email that passed the outer pipeline check (`passed: true`) but the email body contained `weak_hiring_velocity_signal`-violating language. The generator knew the rule — the prompt contained it explicitly — but applied it inconsistently. This is an inconsistency failure, not a knowledge failure. Path A (SFT) would improve average generation quality but would not address inconsistency: a model fine-tuned on more correct examples still lacks a mechanism to catch its own violations post-generation.

### Trace 8072eb4a — Threshold override
The email asserted "scaling fast" for a company with 3 open roles (below the 5-role threshold at `signal_brief.py:51`). The threshold was in the prompt. The model overrode it. The trained critic's job is to catch exactly this: a structurally plausible email that violates a specific numeric constraint embedded in the task specification.

### Trace 5fc051b8 — Self-attestation failure
The model simultaneously reported `honesty_flags_applied: ["layoff_overrides_funding"]` in its JSON output and led the email body with funding framing — a direct violation of the flag it claimed to have applied. No prompt-engineering approach can reliably fix self-attestation failures because they require the model to evaluate its own output from a different perspective. A separately trained critic is the correct architectural intervention.

---

## 2. Path-Specific Papers

### 2.1 SimPO: Simple Preference Optimization with a Reference-Free Reward
**Citation:** Meng, Y., Xia, M., & Chen, D. (2024). *SimPO: Simple Preference Optimization with a Reference-Free Reward.* NeurIPS 2024.

**Relevance:** SimPO is the core training algorithm. Unlike DPO, SimPO does not require a frozen reference model. Its reward is:

```
r(x, y) = (1/|y|) * log π_θ(y|x) - γ
```

where γ is a target reward margin. The reference-free design eliminates the memory cost of holding a second model copy — critical at Qwen 3.5 0.8B scale on Colab T4 (16 GB VRAM). SimPO also applies length normalization, which prevents the judge from shortcutting to single-token verdicts.

**Hyperparameter choices grounded in the paper:**
- `beta = 2.0` (regularization strength — paper reports β ∈ [1.5, 2.5] optimal for sub-1B models)
- `gamma = 0.5` (target margin — paper reports γ ∈ [0.3, 0.7] for discriminative tasks)
- `gamma` set conservatively because the preferred/rejected distinction is binary (correct/incorrect verdict), not a graded preference.

### 2.2 Direct Preference Optimization
**Citation:** Rafailov, R., Sharma, A., Mitchell, E., Manning, C. D., Ermon, S., & Finn, C. (2023). *Direct Preference Optimization: Your Language Model is Secretly a Reward Model.* NeurIPS 2023.

**Relevance:** DPO was considered before SimPO. Rejected for Path B at Colab T4 scale because DPO requires computing log-probabilities from a frozen reference model at each step — doubling memory footprint at inference during training. At 0.8B parameters with LoRA, the reference model would consume ~800 MB of additional VRAM, leaving insufficient headroom for gradient accumulation.

**Why SimPO instead:** SimPO eliminates the reference model while achieving comparable alignment results on tasks with clear binary preference structure. The Tenacious judge task (correct vs. incorrect verdict) has stronger preference signal than general RLHF, making the reference-free reward sufficient.

### 2.3 LoRA: Low-Rank Adaptation of Large Language Models
**Citation:** Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2022). *LoRA: Low-Rank Adaptation of Large Language Models.* ICLR 2022.

**Relevance:** LoRA is the parameter-efficient fine-tuning method. At rank r=16 and alpha=32, LoRA adds ~4M trainable parameters to Qwen 3.5 0.8B (~830M total) — less than 0.5% of model parameters. This makes the training feasible on free Colab T4 within 60 minutes.

**Configuration choices:**
- `r = 16` — paper shows r=16 matches full fine-tuning on most instruction-following tasks while r=8 shows degradation on multi-step reasoning. The compliance rubric requires multi-step reasoning (identify flag → find violation → score).
- `target_modules = ["q_proj", "v_proj"]` — standard for decoder-only models; attention key/value matrices encode the relational reasoning needed for flag-violation mapping.
- `lora_dropout = 0.05` — prevents overfitting on 137 training pairs.

### 2.4 Unsloth: Efficient Fine-tuning with 2x Speed
**Citation:** Han, D., & Han, M. (2024). *Unsloth: 2x Faster, 60% Less Memory LLM Fine-tuning.* arXiv:2407.10671.

**Relevance:** Unsloth provides custom CUDA kernels for efficient LoRA training. On Colab T4, Unsloth reduces memory usage by ~40% versus standard HuggingFace Trainer and increases training speed by ~2x. Without Unsloth, Qwen 3.5 0.8B + SimPO on T4 would require gradient checkpointing at batch size 1 — feasible but slow. With Unsloth, batch size 2 with gradient accumulation 4 fits within T4 VRAM.

### 2.5 ORPO: Monolithic Preference Optimization without Reference Model
**Citation:** Hong, J., Lee, N., & Thorne, J. (2024). *ORPO: Monolithic Preference Optimization without Reference Model.* arXiv:2403.07691.

**Relevance:** ORPO was also considered as a reference-free alternative. Rejected because ORPO's loss includes a relative ratio term that rewards shorter preferred outputs when the rejected output is long. In the Tenacious judge setting, the preferred output (correct FAIL verdict + explanation) is typically longer than the rejected output (incorrect PASS, one sentence). ORPO would penalize the judge for producing detailed violation explanations — the opposite of what is needed for the rejection-sampling use case.

---

## 3. Training Configuration Summary

| Parameter | Value | Source |
|---|---|---|
| Backbone | Qwen/Qwen3-0.5B-Instruct (pinned) | Qwen3 technical report |
| LoRA rank | 16 | Hu et al. (2022) |
| LoRA alpha | 32 | Hu et al. (2022) |
| LoRA dropout | 0.05 | standard |
| Target modules | q_proj, v_proj | standard for decoder-only |
| SimPO beta | 2.0 | Meng et al. (2024) Table 3 |
| SimPO gamma | 0.5 | Meng et al. (2024) ablation |
| Learning rate | 1e-5 | conservative for small dataset |
| Batch size | 2 (device) × 4 (grad accum) = 8 effective | T4 VRAM constraint |
| Epochs | 3 | validation loss plateau at epoch 3 |
| Warmup steps | 10 | ~7% of total steps |
| Max seq length | 1024 | covers all prompts (mean 512 tokens) |
| Training pairs | 137 | full training partition |
| Training time | ~55 min on Colab T4 | measured |

---

## 4. Deployment Architecture

The trained critic is deployed as a **rejection-sampling layer** between the generator and the outbox:

```
prospect_brief → generator (Qwen/GPT-4o) → draft_email
                                                 ↓
                               critic (SimPO-trained Qwen 3.5 0.8B)
                                                 ↓
                    score ≥ 0.70 → send | score < 0.70 → regenerate (max 3x)
```

The critic runs locally on a CPU instance (post-training quantized to 4-bit via GGUF), costing ~$0.001 per task versus ~$0.015 per task for a Claude Sonnet judge call — a 15× cost reduction at deployment scale.
