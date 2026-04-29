# Synthesis Memo: Best Practices and Lessons Learned on Synthetic Data for Language Models

**Paper:** Liu et al., "Best Practices and Lessons Learned on Synthetic Data for Language Models," COLM 2024  
**Author:** Eyobed Feleke  
**Date:** 2026-04-29  
**Memo version:** v1

---

## Summary (one paragraph)

Liu et al. survey synthetic data generation across pretraining, fine-tuning, and evaluation use cases. The core operational finding is a quality-quantity tradeoff: a small number of high-quality synthetic examples consistently outperforms a large number of low-quality ones, with "high quality" defined as factual accuracy, diversity, and alignment with the intended task distribution. The paper introduces three quality filters — heuristic filters (rule-based), model-based filters (using a judge to score generated data), and human-in-the-loop review — and recommends a layered approach. The contamination section identifies "self-reference leakage" as a common failure: generated training data that is semantically equivalent to the evaluation partition inflates benchmark performance without genuine capability improvement.

---

## Specific Design Choice Where I Disagree

**Liu et al. recommend using the same frontier model to both generate and filter synthetic data, citing efficiency and consistency.** The paper's experiments use GPT-4 to generate and a GPT-4 judge to filter for most of their reported results. The authors justify this by noting that GPT-4 is the strongest available model for both tasks.

**My disagreement, grounded in Week 10 evidence and Li et al. (2025):** This approach creates preference leakage when applied to judge training (Path B). If I use Claude to generate both the failing emails and the judge-filtered quality scores, the judge I train will overfit to Claude's quality perception. Probe P-18 (from Week 10) documents the self-attestation failure: the Week 10 agent simultaneously violated a honesty flag and self-reported compliance. A judge trained on data generated and filtered by the same model family will exhibit the same blind spot — it will learn to approve the violations that the generator considers "fine" because the generator was the quality filter.

**My design choice:** I use Claude for hard seed authoring, DeepSeek for bulk variation, and Qwen for quality filtering. The three model families have different priors about what constitutes a "compliant" email — Qwen is more likely to flag a violation that Claude considers acceptable because their safety training and instruction-following characteristics differ. This multi-family approach is more expensive than Liu et al.'s single-model approach (requires three OpenRouter API keys and more orchestration), but it is necessary for judge training data quality.

**Concession where Liu et al. are right:** For the programmatic tasks (parameter sweeps, rule-based generation), single-model self-filtering is fine — there is no semantic judgment required, only structural checking. The Liu et al. approach is appropriate for the 30% of programmatic tasks; the multi-family approach is only necessary for the 25% of multi-LLM synthesis tasks.

---

## Application to Tenacious-Bench

1. **Quality over quantity (LIMA principle):** The paper's findings support the LIMA approach (Zhou et al., NeurIPS 2023) — for the Path B preference training, I target 1,000–2,000 high-quality (chosen, rejected) pairs from the training partition, filtered by the Qwen judge at ≥ 3/5 per dimension. This is the correct approach given the training compute budget (Colab T4, free tier).

2. **Diversity heuristic:** The paper warns against synthetic data clustering — if all generated examples look similar, the model memorizes surface patterns rather than learning the underlying distinction. My authoring mode distribution (30% trace, 30% programmatic, 25% multi-LLM, 15% hand-authored) is a direct application of this principle. The hand-authored adversarial tasks (15%) are the diversity guarantee.

3. **Factual grounding:** The paper's recommendation to ground synthetic data in verified facts directly informed my decision to base all prospect signals on the Week 10 `seed/` corpus (style guide, bench summary, ICP definition) rather than hallucinated facts. Trace-derived tasks use real (anonymized) agent outputs, not invented ones.

4. **Limitation I note:** Liu et al.'s quality metrics (perplexity, diversity scores, factual accuracy probes) are designed for pretraining data. Evaluation dataset quality is a different problem: the relevant quality metrics are rubric coherence, task difficulty calibration, and label reliability — none of which are addressed in the paper. The inter-rater agreement measurement in `inter_rater_agreement.md` is my proxy for evaluation dataset quality, which the paper does not cover.
