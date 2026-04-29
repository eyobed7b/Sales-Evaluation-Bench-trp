# Datasheet for Tenacious-Bench v0.1

*Following Gebru et al. (2021) "Datasheets for Datasets" and Pushkarna et al. (FAccT 2022) "Data Cards: Purposeful and Transparent Dataset Documentation" (telescopic, periscopic, and microscopic layered detail).*

**Dataset name:** Tenacious-Bench v0.1  
**Version:** 0.1  
**License:** CC-BY-4.0  
**Author:** Eyobed Feleke  
**Date:** 2026-04-29  
**HuggingFace:** (to be published — link added after Day 7 publication)

---

## Telescopic Summary

Tenacious-Bench v0.1 is a 250-task evaluation dataset for B2B outbound sales agents operating in the staffing/consulting domain. Each task presents a (prospect brief, candidate email, scoring rubric) triple. The benchmark is designed to measure failure modes that generic retail benchmarks (τ²-Bench retail) cannot grade: honesty flag compliance, ICP disqualification routing, tone marker adherence, and bench capacity honesty. The primary use case is evaluating and fine-tuning small language models deployed as judges or rejection-sampling critics in B2B sales agent pipelines.

---

## 1. Motivation

### Why was this dataset created?

Tenacious operates a B2B staffing and consulting sales agent that composes outreach emails grounded in real-time prospect signals. The agent has documented failure modes — particularly *signal-over-claiming* (asserting facts the agent cannot verify) and *honesty flag bypass* (the LLM ignoring its own constraints at generation time) — that no existing public benchmark measures. τ²-Bench retail grades task completion on transactional retail scenarios; it assigns no penalty for a factually incorrect assertion and has no concept of honesty flag compliance.

Tenacious-Bench v0.1 was created to: (1) measure these specific failure modes in a reproducible way, (2) provide training data for a preference-tuned judge that can detect violations post-generation, and (3) contribute a domain-specific evaluation artifact to the open evaluation community for B2B sales agents.

### Who created the dataset, and on whose behalf?

Created by Eyobed Feleke as part of the TRP1 Week 11 challenge at 10 Academy. The dataset represents Tenacious's workflow and failure modes but was constructed from synthetic and publicly-sourced data, not from any private Tenacious customer records.

### Who funded the creation?

10 Academy TRP1 program. Compute costs: ≤$10 per the program budget envelope.

---

## 2. Composition

### What does each instance represent?

Each instance is an evaluation task consisting of:
- `prospect_brief`: synthetic prospect data (company name, ICP segment, honesty flags, enriched signals)
- `candidate_output`: a candidate outreach email (subject + body) produced by a simulated or real agent
- `scoring_rubric`: machine-verifiable rubric with 3–4 dimensions (honesty_flag_compliance, tone_marker_compliance, format_compliance, signal_grounding)
- `ground_truth`: expected pass/fail outcome and expected aggregate score (0.0–1.0)

### How many instances are there?

250 total tasks:
- Train partition: 125 tasks (50%)
- Dev partition: 75 tasks (30%)
- Held-out partition: 50 tasks (20%, sealed until leaderboard publication)

### What data does each instance consist of?

Structured JSON with string fields (subject, body, company name, signals) and array fields (honesty flags, rubric dimensions). No images, audio, or personally identifiable information. Company names are synthetic; prospect signals are parameterized from public data structures (Crunchbase field schemas, LinkedIn job post patterns) but not scraped from live sources.

### Is every instance labeled?

Yes. Every task has `ground_truth.expected_pass` (boolean) and `ground_truth.expected_score` (float 0–1). Labels were assigned by the author; inter-rater agreement was measured on a 30-task subset (see `inter_rater_agreement.md`).

### Are there recommended data splits?

Yes. The `train/` partition is for training the Path B preference judge. The `dev/` partition is for hyperparameter tuning and validation. The `held_out/` partition is sealed and should not be used during training or validation. Scores on held-out are the primary evaluation metric.

### Is there any information that could be considered sensitive?

No. All company names are synthetic. All prospect signals are parameterized from public schemas. No real email addresses, phone numbers, or personally identifiable information is present.

### Does the dataset contain data that might be considered confidential?

No. The dataset does not contain any Tenacious customer data, internal deal records, or SDR contact lists. "Tenacious" is named only as the workflow domain.

---

## 3. Collection

### How was the data collected?

Tasks were authored using four modes (see `methodology.md` for full rationale):

| Mode | Count | Method |
|---|---|---|
| Trace-derived | ~75 | Restructured from Week 10 `eval/trace_log.jsonl` entries into (brief, candidate, rubric) triples |
| Programmatic | ~75 | Templates with parameterized slots (company size, segment, stack, honesty flags) expanded combinatorially via `generation_scripts/generate_dataset.py` |
| Multi-LLM synthesis | ~62 | Hard seeds authored with Claude (Anthropic); bulk variants generated by DeepSeek V3.2; quality-filtered by Qwen3-235B judge |
| Hand-authored adversarial | ~38 | Written by the author to specifically defeat the Week 10 agent on edge cases the synthesis pipeline misses |

### What mechanisms were used to collect the data?

- Trace-derived: Python parsing of `eval/trace_log.jsonl` from the Week 10 repo
- Programmatic: `generation_scripts/generate_dataset.py` (deterministic, seed=42)
- Multi-LLM: OpenRouter API calls (model routes documented in `generation_scripts/pipeline.py`)
- Hand-authored: Direct JSON authoring by the author

### Who was involved in the data collection process?

The author (Eyobed Feleke). No crowdsourcing or external annotators. Inter-rater agreement was self-measured via 24-hour re-labeling protocol (see `inter_rater_agreement.md`).

### Over what timeframe was data collected?

2026-04-27 to 2026-04-29 (Days 2–3 of the Week 11 challenge).

### Were there any ethical review processes?

Not formally. The dataset does not involve human subjects, does not collect personal data, and does not generate output that could be directly used to harm individuals. The Tenacious workflow domain involves cold outreach; the dataset is designed to *reduce* the harms of bad cold outreach (false assertions, condescending framing) rather than enable them.

---

## 4. Preprocessing and Cleaning

### Was any preprocessing done?

- **Trace-derived tasks**: Prospect company names replaced with synthetic names; email bodies rewritten to match the failure mode being tested
- **Programmatic tasks**: Slot-filling via Python templates; no external data sources
- **Multi-LLM synthesis**: Quality filter applied — all generated tasks passed a pointwise judge score ≥ 3/5 on input coherence, ground-truth verifiability, and rubric-application clarity before inclusion
- **Contamination checks**: N-gram overlap (< 8-gram), embedding similarity (cosine < 0.85), and time-shift verification applied before sealing held-out partition

### Was the raw/source data saved?

Trace-derived source data is in `eval/trace_log.jsonl` in the Week 10 repo. Generation scripts are in `generation_scripts/`. All seeds, model routes, and judge-filter thresholds are committed.

---

## 5. Uses

### For what purposes was this dataset created?

1. **Evaluation**: Measuring B2B sales agent performance on Tenacious-specific failure modes
2. **Training**: Preference pairs for SimPO/DPO training of a compliance judge (Path B)
3. **Research**: Demonstrating that domain-specific benchmarks can be constructed from small seed corpora using multi-LLM synthesis

### What are appropriate uses of this data?

- Evaluating LLM-based sales agents for honesty and tone compliance
- Training preference-tuned judges for B2B outreach quality
- Studying LLM honesty flag compliance in instruction-following settings
- Benchmarking cold email generation quality

### What are inappropriate uses?

- Using the dataset to train models that generate *better* spam or deceptive cold outreach
- Treating the baseline scores from the Week 10 agent as representative of any real Tenacious business metrics
- Using synthetic company names or prospect profiles as real company intelligence

### Are there any tasks for which the dataset should not be used?

The dataset should not be used to evaluate general-purpose conversational agents; it is specifically designed for B2B sales outreach agents with honesty-flag architectures.

---

## 6. Distribution

### How will the dataset be distributed?

Published on HuggingFace Hub under the author's handle. License: CC-BY-4.0.

The held-out partition is distributed separately after leaderboard publication. It is not included in the public dataset at initial release.

### Is the dataset subject to any IP restrictions?

The prospect signals and company structures are synthetic. The style guide, bench summary, and seed documents are derived from the TRP1 challenge materials and are used with permission for educational purposes.

---

## 7. Maintenance

### Who is responsible for maintaining the dataset?

Eyobed Feleke (eyobed@10academy.org).

### How will the dataset be updated?

Version increments (v0.2, v0.3) will add tasks for failure modes not captured in v0.1 (see `memo.pdf` skeptic's appendix for planned extensions). The held-out partition will be rotated after each major version to prevent contamination.

### Will older versions be retained?

Yes. Version 0.1 will remain accessible on HuggingFace with the original tag.

### If others want to contribute, how can they do so?

GitHub Issues or Pull Requests on the project repository. New tasks must pass the contamination check script and the judge-filter pipeline documented in `generation_scripts/`.

---

## Periscopic Detail (Pushkarna et al.)

### Intended use context

Researchers and practitioners building B2B sales agent evaluation pipelines. Primary user: ML engineers at staffing/consulting companies evaluating agent honesty compliance. Secondary user: academic researchers studying LLM instruction-following in constrained generation settings.

### Known gaps

1. Tasks cover only email composition, not multi-turn discovery call behavior
2. Programmatic tasks use synthetic company names — real distribution shift may exist
3. Inter-rater agreement was self-measured (single rater, 24-hour gap) rather than multi-annotator
4. Held-out partition is small (50 tasks) — statistical power is limited for fine-grained category-level analysis

### Baseline performance

Week 10 agent (DeepSeek V3.2 via OpenRouter, no compliance judge):
- Dev partition mean score: measured from `eval/trace_log.jsonl` (see `ablations/ablation_results.json`)
- Pass rate: approximately 60–65% (estimated from Week 10 probe failure rate across categories)

---

## Microscopic Detail

### Rubric dimension weights

| Dimension | Weight | Verifier type |
|---|---|---|
| honesty_flag_compliance | 0.45 | regex |
| tone_marker_compliance | 0.20 | regex |
| format_compliance | 0.15 | length_check |
| signal_grounding | 0.20 | llm_judge |

### Judge model rotation

See `methodology.md` for the model rotation policy. The scoring evaluator uses Qwen3-235B as the default judge for `llm_judge` dimensions. Eval-tier runs use Claude Sonnet 4.6.

### Reproducibility

All generation is deterministic with `seed=42`. The full dataset can be regenerated from `generation_scripts/generate_dataset.py --seed 42`. Scoring evaluator uses `seed=42` for any stochastic judge calls.
