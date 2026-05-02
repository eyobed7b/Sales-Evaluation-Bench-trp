# Tenacious-Bench v0.1

**Sales Agent Evaluation Benchmark for B2B Outbound Honesty and Tone Compliance**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Author:** Eyobed Feleke (eyobed@10academy.org)  
**Status:** Week 11 Final Submission — Acts I–IV complete  
**Submission deadline:** Saturday 2026-05-02, 21hr UTC

**Public artifacts:**
- HuggingFace dataset: [`eyobed7b/tenacious-bench`](https://huggingface.co/datasets/eyobed7b/tenacious-bench)
- HuggingFace model: [`eyobed7b/tenacious-bench-simpo-judge-v1`](https://huggingface.co/eyobed7b/tenacious-bench-simpo-judge-v1)
- Blog post: [LinkedIn — Tenacious-Bench v0.1](https://www.linkedin.com/feed/update/urn:li:activity:7456391267724349440/)

---

## Overview

Tenacious-Bench v0.1 is a 274-task evaluation dataset for B2B outbound sales agents (250 programmatic + 24 hand-authored from Style Guide v2). It measures failure modes that generic benchmarks (τ²-Bench retail) cannot grade:

- **Honesty flag compliance** — does the agent respect constraints like `weak_hiring_velocity_signal` and `layoff_overrides_funding` at generation time?
- **ICP disqualification routing** — does the agent suppress outreach to prospects that meet documented disqualifying conditions?
- **Tone marker adherence** — does the email avoid exclamation marks, buzzwords, condescending framing, and over-length?
- **Signal grounding** — does the email reference at least one verified prospect-specific signal?

Every task has a machine-verifiable rubric. The scoring evaluator runs without human intervention.

---

## Repository Structure

```
Sales-Evaluation-Bench-trp/
├── memo.md                            ← FINAL REPORT (2-page decision memo)
├── evidence_graph.json                ← Every numeric claim mapped to source file
├── README.md
├── audit_memo.md                      ← Act I: what τ²-Bench misses (600 words)
├── methodology.md                     ← Path B declaration + justification
├── methodology_rationale.md          ← Path-specific papers (SimPO, LoRA, DPO, ORPO)
├── schema.json                        ← Task schema + 3 example tasks
├── scoring_evaluator.py               ← Machine-verifiable scoring script
├── datasheet.md                       ← Gebru + Pushkarna dataset documentation
├── contamination_check.json           ← N-gram, embedding, time-shift results
├── inter_rater_agreement.md           ← Self-labeling κ scores per rubric dimension
├── cost_log.md                        ← All API and compute charges
├── seed/
│   └── style_guide_v2.md             ← Tenacious Style Guide v2 (24 labeled drafts)
├── training_data/
│   ├── build_simpo_pairs.py           ← Generates SimPO preference pairs
│   └── simpo_pairs.jsonl              ← 137 preference pairs (84 FAIL + 53 PASS)
├── training/
│   ├── train_simpo.py                 ← Unsloth + TRL SimPO training script
│   ├── hyperparameters.json           ← Full run config + timing
│   └── loss_log.json                  ← Per-step training loss (55 min on Colab T4)
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
    ├── memo_simpo_preference_optimization.md  ← Meng et al. (NeurIPS 2024) [PATH-SPECIFIC]
    └── memo_lora_efficient_finetuning.md      ← Hu et al. (ICLR 2022) [PATH-SPECIFIC]
```

---

## Quickstart — Reproduce the Headline Score

```bash
# 1. Clone and install
git clone <repo-url>
cd Sales-Evaluation-Bench-trp
pip install -r requirements.txt   # transformers, peft, trl, datasets, accelerate

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

Expected output for dev partition (rule-only, no trained judge):
```
Scored 82 tasks
Mean score:   ~0.78
Pass rate:    ~0.66
Accuracy:     ~0.74
```

**Held-out headline results (SimPO judge v1):**

| Condition | Accuracy | Cost/task |
|---|---|---|
| Rule-only | 69.1% | $0.000 |
| SimPO judge (trained) | 92.7% | $0.000 |
| Delta A | +23.6pp (p=0.004) | — |

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

## Training Path

**Path B — SimPO preference-tuned judge/critic**

The judge is trained to detect honesty flag violations post-generation and serve as a rejection-sampling layer. Backbone: Qwen 3.5 0.8B with LoRA. Training: Unsloth on Google Colab T4 (free).

Evidence for Path B over Path A/C: see `methodology.md` and `probes/target_failure_mode.md` in the Week 10 repo.

Training runs and ablation results will be committed to `training/` and `ablations/` by the final submission (Saturday 2026-05-02).

---

## What Is Next (Days 4–7)

- [ ] Day 4: Format training partition as SimPO preference pairs; path-specific papers read
- [ ] Day 5: Core training run (Qwen 3.5 0.8B + LoRA via Unsloth, ~60 min on Colab T4)
- [ ] Day 6: Ablations (Delta A vs. baseline, Delta B vs. prompt-engineering, Cost-Pareto)
- [ ] Day 7: Publish dataset to HuggingFace; publish LoRA adapter; write blog post; community engagement

---

## Key Files for Grading

| Grading dimension | File |
|---|---|
| Benchmark design | `audit_memo.md`, `schema.json` |
| Machine-verifiable scoring | `scoring_evaluator.py` |
| Dataset quality | `datasheet.md`, `inter_rater_agreement.md` |
| Contamination prevention | `contamination_check.json`, `generation_scripts/contamination_check.py` |
| Methodology rationale | `methodology.md` |
| Multi-LLM synthesis routing | `generation_scripts/generate_dataset.py`, `synthesis_memos/` |
| Tone compliance spec | `seed/style_guide_v2.md` |
| Cost discipline | `cost_log.md` |

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
