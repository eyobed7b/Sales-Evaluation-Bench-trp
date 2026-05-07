# Tenacious-Bench v0.1 — Final Evaluation Memo
**Author:** Eyobed Feleke · eyobed@10academy.org · 2026-05-02

---

## Page 1 — The Decision

### Executive Summary

A SimPO-trained Qwen 3.5 0.8B judge, fine-tuned on 137 Tenacious-Bench preference pairs, correctly classifies **92.7%** of held-out compliance tasks (51/55) versus **69.1%** for the rule-only baseline — a **+23.6pp gain (95% CI: [+9.8, +37.4], McNemar p=0.004)** — while adding zero marginal cost at inference. The trained judge closes three of the four documented Week 10 failure modes (honesty flag bypass, bench overcommitment, tone drift) but still requires the rule-based layer for scheduling and format checks; the recommended deployment is a hybrid: rule-only as a hard gate, SimPO judge as the semantic layer, with a human-review trigger for low-confidence outputs.

### Headline Lift — Delta A

| Condition | Held-out Accuracy | Held-out Pass Rate | Cost / task |
|---|---:|---:|---:|
| Rule-only baseline | 69.1% (38/55) | 61.8% | $0.000 |
| Prompt-engineering (3-shot Haiku) | 78.2% (43/55) | 65.5% | $0.001 |
| **SimPO judge v1** | **92.7% (51/55)** | **67.3%** | **$0.000** |
| (Claude Sonnet API, est.) | ~96.0% | ~68% | $0.003 |

**Delta A = +23.6pp** over rule-only (95% CI: [+9.8pp, +37.4pp], McNemar χ²=8.47, p=0.004).

Largest per-category gains: multithread-leakage +70pp, cost-pathology +50pp, dual-control +38pp. These are the three categories that require semantic flag-violation mapping — exactly the failure modes Path B was designed to address.

### Delta B — Honest Report

**Delta B = +14.5pp** over 3-shot prompt-engineering (95% CI: [+1.6pp, +27.4pp], McNemar p=0.043). The improvement is statistically significant but the lower bound (+1.6pp) is near zero — a stronger few-shot baseline (Claude Sonnet, 8 examples) would likely narrow this gap further. The advantage of the trained judge over prompt-engineering is not accuracy alone: it is **cost**. The prompt-engineering approach costs $0.001/task and degrades on edge cases (it has not seen the specific flag combinations in the training partition). The SimPO judge runs at $0.000/task and was trained on the exact violation types in the Tenacious domain.

### Cost Per Task

| Mode | Cost/task | Cost/1k tasks | Notes |
|---|---:|---:|---|
| Rule-only | $0.000 | $0.00 | No API call |
| SimPO judge (local 4-bit) | $0.000 | $0.00 | Runs on CPU after quantization |
| Prompt-eng (Claude Haiku) | $0.001 | $0.80 | 3-shot, ~800 tokens/call |
| Claude Sonnet judge | $0.003 | $3.30 | Full eval-tier, not deployed |

At 10,000 outreach emails/month, the SimPO judge delivers **$0/month** versus **$33/month** for a Claude Sonnet judge at comparable (though not identical) accuracy.

### Deployment Recommendation

**Deploy with caveat.**

Deploy the hybrid system: (1) rule-only hard gate for format/length/banned-phrase violations, (2) SimPO judge for semantic compliance (honesty flags, signal grounding), (3) human-review queue for any task where judge score is in the uncertainty band [0.60–0.75]. The caveat: the judge was trained on 137 pairs — half the minimum recommended by Liu et al. (2024) for this task complexity. ICP misclassification accuracy (96%) masks the fact that the judge has not seen enough diverse disqualification scenarios. Deploy on the four high-confidence categories (signal-overclaiming, tone-drift, bench-overcommitment, dual-control) first; gate ICP misclassification behind the human-review queue until training data doubles.

---

## Page 2 — The Skeptic's Appendix

### Four Failure Modes Tenacious-Bench v0.1 Still Does Not Capture

**1. Multi-turn context degradation.** All 274 tasks are single-turn (brief → email). Tenacious agents operating in a thread context (follow-up 2, follow-up 3) accumulate prior context that can override the active honesty flags. A prospect who responded "we're not hiring right now" in turn 1 should trigger a `prospect_stated_no_hiring` flag in turn 2; the current benchmark does not model this. v0.2 addition: multi-turn trace tasks with session-state honesty flags.

**2. Cross-prospect data leakage.** When an agent processes briefs for multiple prospects in a batch, embeddings or context from prospect A can leak into the email drafted for prospect B — particularly in systems using shared KV caches. No task in v0.1 tests for cross-contamination. v0.2 addition: paired tasks where the second task's brief contains a signal that should only be present in the first.

**3. Partial flag acknowledgment.** The rubric currently marks a task FAIL if any banned pattern from an active flag appears. A more granular failure mode is *partial acknowledgment*: the agent correctly hedges one flag ("we saw some hiring signal") while ignoring a second active flag (`layoff_overrides_funding`). The current binary FAIL verdict does not distinguish "ignored all flags" from "ignored one of three flags." v0.2 addition: per-flag scoring with a minimum-satisfied-flags threshold.

**4. Prospect response simulation.** The benchmark evaluates the outbound email in isolation. It does not assess whether a compliant email is likely to elicit a positive response — the downstream business metric. An email can be fully compliant (score 1.0) and still be a weak opener with low conversion probability. v0.2 addition: a prospect-response simulator that rates conversion likelihood independently of compliance.

### Public-Signal Lossiness in Ground Truth

The hiring signals, AI maturity scores, and leadership signals in all tasks are synthetic parameters drawn from public data *schemas* (Crunchbase field structures, LinkedIn job post patterns) but not from live scrapes. This means: (a) the benchmark does not test whether the agent correctly handles signal staleness (a hiring signal that was true 6 months ago but is no longer active), and (b) the AI maturity score is a numeric placeholder, not a real inferred score from a production signal pipeline. Ground truth labels are reliable for the rubric dimensions as written, but the rubric itself does not capture signal temporality. Any agent that correctly handles the synthetic signals will still need separate evaluation on live-signal inputs before production deployment.

### One Honest Unresolved Training Failure

The CPO judge has a **PASS bias on ICP misclassification tasks** (18% false-negative rate on disqualification-category held-out tasks). The root cause has two components:

**Structural cause — output length asymmetry under the CPO loss.** PASS verdicts in the training pairs average ~11 tokens; FAIL verdicts with reasoning average ~54 tokens. The CPO loss uses raw summed log-probability as the reward. Longer sequences accumulate more negative log-probability regardless of quality, creating a length confound that works against the FAIL > PASS preference signal on short PASS outputs. This is separate from β and would persist even with a lower β value.

**Training cause — β=2.0 may over-regularize on sparse disqualification pairs.** β is the preference-pressure scalar: higher β pulls the trained policy back toward the base model's priors more strongly after each update. With only 84 fail-case training pairs (including ~10 disqualification tasks), the base model's generosity prior competes against the FAIL > PASS signal and may not be fully overridden. This is a β/data-size interaction, not a pure β problem.

**Diagnostic plan before retraining (cheapest first):**
1. Run `scoring_evaluator.py --batch tenacious_bench_v0.1/held_out/` — new `false_pass_rate_on_expected_fail` and `category_recall_on_expected_fail` fields now report the bias per category.
2. Raise PASS threshold from 0.70 to 0.75 in `score_task()` and re-score. If false-negative rate on disqualification drops below 10%, threshold calibration is sufficient — no retraining needed.
3. If threshold is insufficient: equalize PASS/FAIL output lengths in `build_simpo_pairs.py`, then retrain with `loss_type="simpo"` and `gamma_beta_ratio=0.4` in `train_simpo.py`.
4. Only lower β (try 1.0) if Step 3 does not close the gap — β is a global knob and risks degrading calibration on non-disqualification categories.

This failure mode requires a separate ICP classifier gate upstream of the email judge as a structural fix independent of retraining.

### Kill-Switch Trigger Condition

**Trigger the kill-switch and revert to rule-only if any of the following are observed in production:**

1. The judge's false-negative rate on `layoff_overrides_funding` violations exceeds **5%** over a 7-day rolling window (measured via weekly audit of 50 randomly sampled judge-approved emails). A `layoff_overrides_funding` false negative sends a growth pitch to a company in active workforce reduction — a direct reputational risk.

2. The judge approves any email containing a **specific banned phrase from Style Guide v2** that also appears in a `tone-drift` violation documented in the training data. This would indicate the judge has regressed on a pattern it should have learned.

3. **Classification accuracy on the dev partition drops below 70%** after any model update or quantization change — measured by running `scoring_evaluator.py --batch tenacious_bench_v0.1/dev/ --no-llm` on the merged weights before deployment.

---

*All numeric claims mapped to source files in `evidence_graph.json`.*  
*Full methodology: `methodology_rationale.md`. Training artifacts: `training/`. Ablations: `ablations/`.*
