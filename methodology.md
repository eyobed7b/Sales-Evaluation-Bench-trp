# Methodology: Tenacious-Bench v0.1

**Author:** Eyobed Feleke  
**Date:** 2026-04-29  
**Version:** 0.1

---

## Path Declaration

**Path B — DPO/SimPO/ORPO preference-tuned judge or critic**

### Justification (citing Week 10 evidence)

My Week 10 failure taxonomy ranks Signal-Over-claiming and Dual-Control as joint top failure modes (combined score 25/25 each). The evidence for choosing Path B over Path A or C is:

**Evidence from trace_id cf06a98e:** The agent composed an email that passed the outer pipeline check (`passed: true`) but the email body contained `weak_hiring_velocity_signal`-violating language. The generator produced a compliant-looking email structurally (correct format, JSON parseable) while violating a semantic constraint. This is the hallmark of an *inconsistency* failure, not a *generation quality* failure — the generator knows the rules and applies them sometimes, but cannot reliably detect when it breaks them.

**Evidence from trace_id 8072eb4a (`passed: false`):** The email asserted "scaling fast" for a company with 3 open roles (below the 5-role threshold). The generator had the threshold information in the prompt. It chose to override it. A judge trained to detect this class of violation would have caught it; a better generator might still occasionally produce it under different brief conditions.

**Evidence from trace_id 5fc051b8 (`passed: false`):** The layoff_overrides_funding constraint was violated — the email led with funding framing despite an active layoff signal. The generator self-reported `honesty_flags_applied: ["layoff_overrides_funding"]` in its JSON while the body violated the constraint. This is a self-attestation failure — the generator cannot accurately assess its own output.

**Path B is appropriate because:** The failures are inconsistency failures — the agent gets it right most of the time but cannot tell when it is wrong. Path A (SFT) would improve the average generation quality but would not address the fundamental gap: the absence of a second-layer check that can reliably detect violations post-generation. Path B trains exactly that second layer. The trained critic is deployed as a rejection-sampling layer that scores the generator's output and triggers regeneration when violations are detected — directly addressing the architectural gap identified in `probes/target_failure_mode.md:Section 5`.

**Path A was rejected because:** My Week 10 evidence shows generation *quality* is adequate (the generator produces grammatically correct, often compliant emails); the gap is in *consistency* and *self-assessment*. Fine-tuning the generator on more examples of correct output would not fix the self-attestation failure (P-18) or the post-generation validation absence (P-16).

**Path C was rejected because:** Process reward models require stepwise trajectory labels, and my traces are single-turn (brief → email) rather than multi-turn conversation trajectories. The data prep cost for Path C would be prohibitive given the trace structure.

---

## Training Algorithm: SimPO

**SimPO chosen over DPO.** SimPO (Meng, Xia, Chen, NeurIPS 2024) is reference-free — it does not require computing log-probabilities from a frozen reference model at each training step. At LoRA scale (Qwen 3.5 0.8B on Colab T4), the memory and compute savings of eliminating the reference model forward pass are significant. DPO requires holding the reference model in memory alongside the training model; SimPO does not. ORPO was also considered but SimPO's length-normalization reward avoids ORPO's tendency to reward shorter outputs, which would be problematic for a judge that needs to output structured explanations.

**Backbone:** Qwen 3.5 0.8B (pinned to the version available at time of training — see `training/requirements.txt`).

---

## Partitioning Protocol

Total tasks: 250  
- Train partition: 125 tasks (50%) — `tenacious_bench_v0.1/train/`
- Dev partition: 75 tasks (30%) — `tenacious_bench_v0.1/dev/`
- Held-out partition: 50 tasks (20%) — `tenacious_bench_v0.1/held_out/` (sealed)

Stratification: each partition maintains the same proportional distribution across:
- `failure_category` (10 categories)
- `difficulty` (easy / medium / hard)
- `source_mode` (trace-derived / programmatic / multi-llm-synthesis / hand-authored)

Held-out partition is gitignored from training scripts. It will not be decrypted until after the leaderboard is published.

---

## Contamination Prevention

Three checks applied before any task enters the held-out partition:

1. **N-gram overlap:** No held-out task shares an 8-gram sequence on `body` or `subject` fields with any training task. Checked via `generation_scripts/contamination_check.py`.

2. **Embedding similarity:** Cosine similarity between any held-out task's `body` embedding and any training task's `body` embedding must be < 0.85. Uses `sentence-transformers/all-MiniLM-L6-v2` (free, runs locally).

3. **Time-shift verification:** Any task referencing a specific company signal (e.g., "layoff 45 days ago") uses synthetic companies with parameterized dates, not real companies scraped at a fixed date.

Results committed to `contamination_check.json`.

---

## LLM Rotation Policy (Preference Leakage Prevention)

To avoid preference leakage (Li et al., 2025), no task is generated and judged by the same model family:

| Role | Model family | Used for |
|---|---|---|
| Hard seed authoring | Claude (Anthropic) | Generating the 30–50 hardest multi-LLM synthesis seeds |
| Bulk variation generation | DeepSeek V3.2 via OpenRouter | Expanding seeds into parameter variants |
| Quality filter judge | Qwen3-235B via OpenRouter | Filtering bulk variants before dataset inclusion |
| Spot-check calibration | Claude (Anthropic) | Checking 50 sampled tasks for judge calibration |
| Eval-tier judge (held-out) | Claude Sonnet 4.6 | Sealed-slice scoring only |

Generation and judging never use the same model on the same task. The rotation policy is enforced in `generation_scripts/pipeline.py` via `assert generator_model != judge_model`.

---

## Inter-Rater Agreement Protocol

30 tasks hand-labeled by the author against the rubric. Re-labeled 24 hours later without consulting first labels. Agreement computed per rubric dimension using Cohen's κ. Dimensions below 80% agreement triggered rubric revision before the dataset was finalized. See `inter_rater_agreement.md` for the full agreement matrix.

---

## Authoring Mode Distribution

| Mode | Target share | Actual count |
|---|---|---|
| Trace-derived | 30% | 75 |
| Programmatic | 30% | 75 |
| Multi-LLM synthesis | 25% | 62 |
| Hand-authored adversarial | 15% | 38 |
| **Total** | **100%** | **250** |

Trace-derived tasks are sourced from `eval/trace_log.jsonl` in the Week 10 repo, redacted of any Tenacious-internal identifiers and restructured into (brief, candidate_output, rubric) triples.

---

## Failure Category Distribution

| Category | Tasks | % |
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
| **Total** | **250** | **100%** |

Weighting reflects the ranked table in `probes/failure_taxonomy.md` — higher-priority failure modes receive more tasks to ensure statistical power in the held-out evaluation.
