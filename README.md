# Tenacious-Bench v0.1

**Sales Agent Evaluation Benchmark for B2B Outbound Honesty and Tone Compliance**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Dataset](https://img.shields.io/badge/HuggingFace-Dataset-yellow)](https://huggingface.co/datasets/eyobed7b/tenacious-bench)
[![Model](https://img.shields.io/badge/HuggingFace-Model-blue)](https://huggingface.co/eyobed7b/tenacious-bench-simpo-judge-v1)

**Author:** Eyobed Feleke (eyobed@10academy.org)  
**Status:** Week 11 Final Submission — complete

**Public artifacts:**
- Dataset: [`eyobed7b/tenacious-bench`](https://huggingface.co/datasets/eyobed7b/tenacious-bench)
- Model: [`eyobed7b/tenacious-bench-simpo-judge-v1`](https://huggingface.co/eyobed7b/tenacious-bench-simpo-judge-v1)
- Blog post: [LinkedIn — Tenacious-Bench v0.1](https://www.linkedin.com/feed/update/urn:li:activity:7456391267724349440/)
- Community: [GitHub Issues — feedback welcome](https://github.com/eyobed7b/Sales-Evaluation-Bench-trp/issues/1)
- Final report: [`memo.pdf`](memo.pdf)

---

## Overview

Tenacious-Bench v0.1 is a 274-task evaluation dataset for B2B outbound sales agents (250 programmatic + 24 hand-authored from Style Guide v2). It measures failure modes that generic benchmarks (τ²-Bench retail) cannot grade:

- **Honesty flag compliance** — does the agent respect constraints like `weak_hiring_velocity_signal` and `layoff_overrides_funding` at generation time?
- **ICP disqualification routing** — does the agent suppress outreach to prospects that meet documented disqualifying conditions?
- **Tone marker adherence** — does the email avoid exclamation marks, buzzwords, condescending framing, and over-length?
- **Signal grounding** — does the email reference at least one verified prospect-specific signal?

Every task has a machine-verifiable rubric. The scoring evaluator runs without human intervention.

---

## Headline Results

| Condition | Held-out Accuracy | Cost/task |
|---|---|---|
| Rule-only baseline | 69.1% (38/55) | $0.000 |
| Prompt-eng (3-shot Haiku) | 78.2% (43/55) | $0.001 |
| **CPO judge v1 (trained)** | **92.7% (51/55)** | **$0.000** |
| Claude Sonnet (est.) | ~96.0% | $0.003 |

**Delta A = +23.6 pp** over rule-only (95% CI: [+9.8, +37.4], McNemar p=0.004)  
**Delta B = +14.5 pp** over prompt-engineering (95% CI: [+1.6, +27.4], McNemar p=0.043)

---

## Quickstart — Reproduce the Headline Score

```bash
# 1. Clone and install
git clone https://github.com/eyobed7b/Sales-Evaluation-Bench-trp.git
cd Sales-Evaluation-Bench-trp
pip install -r requirements.txt

# 2. Score the dev partition (no LLM judge — regex + length checks only)
python scoring_evaluator.py \
    --batch tenacious_bench_v0.1/dev/ \
    --output results_dev.json \
    --no-llm

# 3. Score with LLM judge (requires OPENROUTER_API_KEY)
export OPENROUTER_API_KEY=your_key_here
python scoring_evaluator.py \
    --batch tenacious_bench_v0.1/dev/ \
    --output results_dev_full.json

# 4. Regenerate the dataset from scratch (deterministic, seed=42)
python generation_scripts/generate_dataset.py \
    --output tenacious_bench_v0.1/ \
    --seed 42
```

Expected output for dev partition (rule-only):
```
Scored 82 tasks
Mean score:   ~0.78
Pass rate:    ~0.66
Accuracy:     ~0.74
```

A stranger should be able to run this and reproduce a score within 2 percentage points.

---

## Dataset Summary

| Partition | Tasks | Pass rate (expected) |
|---|---|---|
| train | 137 | ~62% |
| dev | 82 | ~61% |
| held_out | 55 | ~60% (sealed) |

**Failure category distribution:**

| Category | Count | Weight |
|---|---|---|
| signal-overclaiming | 60 | 24% |
| icp-misclassification | 45 | 18% |
| dual-control | 30 | 12% |
| bench-overcommitment | 30 | 12% |
| tone-drift | 25 | 10% |
| gap-overclaiming | 20 | 8% |
| signal-reliability | 15 | 6% |
| cost-pathology | 10 | 4% |
| multithread-leakage | 10 | 4% |
| scheduling | 5 | 2% |

---

## Training

**CPO preference-tuned judge — Qwen2.5-0.5B-Instruct + LoRA**

The judge is trained to detect honesty flag violations post-generation and serve as a rejection-sampling layer. Training uses CPO (Contrastive Preference Optimization) — reference-free, no frozen reference model required — on 137 preference pairs via Unsloth on Google Colab T4 (free tier).

| Config | Value |
|---|---|
| Backbone | Qwen/Qwen2.5-0.5B-Instruct |
| LoRA r / alpha | 16 / 32 |
| Target modules | q_proj, v_proj, k_proj, o_proj |
| CPO β | 2.0 |
| Epochs | 3 |
| Training pairs | 137 |
| Final loss | 14.09 |
| Compute | Colab T4 free tier |

---

## Repository Structure

```
Sales-Evaluation-Bench-trp/
├── memo.pdf                           ← FINAL REPORT (2-page decision memo)
├── memo.md                            ← Source for memo.pdf
├── evidence_graph.json                ← Every numeric claim mapped to source file
├── audit_memo.md                      ← Act I: what τ²-Bench misses
├── methodology.md                     ← Path B declaration + justification
├── methodology_rationale.md           ← Path-specific papers (CPO, LoRA, SimPO, DPO)
├── schema.json                        ← Task schema + 3 example tasks
├── scoring_evaluator.py               ← Machine-verifiable scoring script
├── datasheet.md                       ← Gebru + Pushkarna dataset documentation
├── contamination_check.json           ← N-gram, embedding, time-shift results
├── inter_rater_agreement.md           ← Self-labeling κ scores per rubric dimension
├── cost_log.md                        ← All API and compute charges
├── seed/
│   └── style_guide_v2.md             ← Tenacious Style Guide v2 (24 labeled drafts)
├── training_data/
│   ├── build_simpo_pairs.py           ← Generates preference pairs
│   └── simpo_pairs.jsonl              ← 137 preference pairs (84 FAIL + 53 PASS)
├── training/
│   ├── train_simpo.py                 ← Unsloth + TRL CPO training script
│   ├── hyperparameters.json           ← Full run config + timing
│   └── loss_log.json                  ← Per-step training loss (Colab T4)
├── ablations/
│   ├── ablation_results.json          ← Delta A (+23.6pp), Delta B (+14.5pp), cost-Pareto
│   ├── held_out_traces.jsonl          ← Sample held-out scoring traces
│   └── statistical_test.json          ← McNemar test + bootstrap CIs
├── tenacious_bench_v0.1/
│   ├── manifest.json
│   ├── train/tasks.jsonl              ← 137 tasks (50%)
│   ├── dev/tasks.jsonl                ← 82 tasks (30%)
│   └── held_out/tasks.jsonl           ← 55 tasks (20%, sealed)
├── generation_scripts/
│   ├── generate_dataset.py            ← Reproducible generation (seed=42)
│   └── contamination_check.py
└── synthesis_memos/
    ├── memo_llm_as_judge_survey.md    ← Gu et al. (2024–2025)
    ├── memo_synthetic_data_best_practices.md  ← Liu et al. (COLM 2024)
    ├── memo_simpo_preference_optimization.md  ← Meng et al. (NeurIPS 2024)
    └── memo_lora_efficient_finetuning.md      ← Hu et al. (ICLR 2022)
```

---

## Key Files for Grading

| Grading dimension | File |
|---|---|
| Benchmark design | `audit_memo.md`, `schema.json` |
| Machine-verifiable scoring | `scoring_evaluator.py` |
| Dataset quality | `datasheet.md`, `inter_rater_agreement.md` |
| Contamination prevention | `contamination_check.json`, `generation_scripts/contamination_check.py` |
| Methodology rationale | `methodology.md`, `methodology_rationale.md` |
| Multi-LLM synthesis routing | `generation_scripts/generate_dataset.py`, `synthesis_memos/` |
| Tone compliance spec | `seed/style_guide_v2.md` |
| Training artifacts | `training/`, `ablations/` |
| Cost discipline | `cost_log.md` |
| Final decision memo | `memo.pdf` |

---

## License

CC-BY-4.0. See `LICENSE` for details.

---

## Citation

```
@dataset{feleke2026tenacious,
  title={Tenacious-Bench v0.1: A Sales Agent Evaluation Benchmark for B2B Outbound Honesty Compliance},
  author={Feleke, Eyobed},
  year={2026},
  url={https://huggingface.co/datasets/eyobed7b/tenacious-bench}
}
```
