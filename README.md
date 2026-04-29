# Tenacious-Bench v0.1

**Sales Agent Evaluation Benchmark for B2B Outbound Honesty and Tone Compliance**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Author:** Eyobed Feleke (eyobed@10academy.org)  
**Status:** Week 11 Interim Submission — Acts I & II complete  
**Submission deadline:** Wednesday 2026-04-29, 21hr UTC

---

## Overview

Tenacious-Bench v0.1 is a 250-task evaluation dataset for B2B outbound sales agents. It measures failure modes that generic benchmarks (τ²-Bench retail) cannot grade:

- **Honesty flag compliance** — does the agent respect constraints like `weak_hiring_velocity_signal` and `layoff_overrides_funding` at generation time?
- **ICP disqualification routing** — does the agent suppress outreach to prospects that meet documented disqualifying conditions?
- **Tone marker adherence** — does the email avoid exclamation marks, buzzwords, condescending framing, and over-length?
- **Signal grounding** — does the email reference at least one verified prospect-specific signal?

Every task has a machine-verifiable rubric. The scoring evaluator runs without human intervention.

---

## Repository Structure

```
Sales-Evaluation-Bench-trp/
├── README.md                          ← this file
├── audit_memo.md                      ← Act I: what τ²-Bench misses (600 words)
├── schema.json                        ← Task schema + 3 example tasks
├── scoring_evaluator.py               ← Machine-verifiable scoring script
├── methodology.md                     ← Path B declaration + justification
├── datasheet.md                       ← Gebru + Pushkarna dataset documentation
├── contamination_check.json           ← N-gram, embedding, time-shift results
├── inter_rater_agreement.md           ← Self-labeling κ scores per rubric dimension
├── cost_log.md                        ← All API and compute charges
├── tenacious_bench_v0.1/
│   ├── manifest.json                  ← Dataset manifest (counts, seed, distribution)
│   ├── train/tasks.jsonl              ← 125 training tasks (50%)
│   ├── dev/tasks.jsonl                ← 75 dev tasks (30%)
│   └── held_out/tasks.jsonl           ← 50 held-out tasks (20%, sealed)
├── generation_scripts/
│   ├── generate_dataset.py            ← Reproducible dataset generation (seed=42)
│   └── contamination_check.py        ← Contamination check script
└── synthesis_memos/
    ├── memo_llm_as_judge_survey.md    ← Gu et al. (2024–2025) synthesis
    └── memo_synthetic_data_best_practices.md  ← Liu et al. (COLM 2024) synthesis
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

Expected output for dev partition (Week 10 baseline, no trained judge):
```
Scored 75 tasks
Mean score:   ~0.52
Pass rate:    ~0.61
Accuracy:     ~0.68
```

A stranger should be able to run this and reproduce a score within 2 percentage points.

---

## Dataset Summary

| Partition | Tasks | Pass rate (expected) |
|---|---|---|
| train | 125 | ~62% |
| dev | 75 | ~61% |
| held_out | 50 | ~60% (sealed) |

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
