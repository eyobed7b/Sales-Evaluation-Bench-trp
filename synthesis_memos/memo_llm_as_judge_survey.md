# Synthesis Memo: A Survey on LLM-as-a-Judge

**Paper:** Gu et al., "A Survey on LLM-as-a-Judge," 2024–2025 (latest revision)  
**Author:** Eyobed Feleke  
**Date:** 2026-04-28  
**Memo version:** v1

---

## Summary (one paragraph)

The survey catalogs LLM-as-a-Judge patterns across three dimensions: evaluation granularity (pointwise, pairwise, listwise), evaluation process (score-based, critique-based, debate-based), and failure modes (position bias, verbosity bias, self-enhancement bias, preference leakage). The authors find that small open-source judge models trained from preferences can approach frontier judge performance on well-defined rubrics, particularly when the rubric dimensions are narrow and verifiable. The key operational insight is that judge reliability degrades when the judge and generator share training distribution — a pattern the authors call "preference leakage" (separately expanded by Li et al., 2025).

---

## Specific Design Choice Where I Disagree

**The survey recommends pairwise evaluation as the most reliable format for quality assessment.** The survey's evidence for pairwise superiority over pointwise comes primarily from open-ended generation tasks (story writing, instruction following) where the quality dimension is holistic. For Tenacious-Bench, I designed a pointwise rubric rather than a pairwise one, and I think this is correct for the following reason:

**My disagreement, grounded in Week 10 evidence:** The Tenacious failure modes (honesty flag compliance, tone markers, format compliance) are not holistic quality assessments — they are discrete, verifiable binary conditions. Probe P-16 documents that the Week 10 agent's honesty flags are violated or not violated in ways that can be checked by regex or a narrow semantic call. There is no meaningful "this email is better than that email on tone" assessment — the question is "does this email contain 'aggressively hiring' when weak_hiring_velocity_signal is active?" A pairwise comparison would introduce unnecessary complexity and would make the rubric harder to machine-verify.

**Concession:** For the `signal_grounding` dimension (which measures whether the email references prospect-specific signals), a pairwise comparison might improve inter-rater agreement (my self-κ of 0.68 on this dimension suggests it is underspecified for pointwise scoring). I will add an example-anchored rubric in v0.2 rather than switch to pairwise, since machine-verifiability is a binding constraint.

---

## Application to Tenacious-Bench

1. **Judge model rotation:** The survey's section on preference leakage directly informed my decision to use different model families for generation and judging (see `methodology.md` model rotation policy). I apply this strictly: Claude generates seeds; Qwen judges; DeepSeek generates bulk; Claude spot-checks.

2. **Pointwise scoring with 1–5 scale:** The survey's recommendation for a rubric-grounded pointwise scale is implemented in the judge quality filter — each generated task is scored 1–5 on input coherence, ground-truth verifiability, and rubric-application clarity. Threshold ≥ 3 for inclusion.

3. **Position bias:** For tasks with multiple rubric dimensions, the survey warns that LLM judges assign higher scores to dimensions presented first. I mitigate this by always ordering dimensions: honesty_flag_compliance → tone_marker_compliance → format_compliance → signal_grounding (from most objective to most subjective). The judge sees the most verifiable dimension first.

4. **Limitation I note:** The survey does not specifically address B2B sales domain evaluation. Its findings on judge reliability are primarily from academic writing, code, and math tasks. Generalization to domain-specific business writing evaluation is an open question — one that Tenacious-Bench v0.1 is positioned to answer.
