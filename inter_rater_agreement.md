# Inter-Rater Agreement Report

**Protocol:** 30-task subset labeled by the author, then re-labeled 24 hours later without consulting first labels.  
**Date of first labeling:** 2026-04-28  
**Date of re-labeling:** 2026-04-29  
**Labeler:** Eyobed Feleke

---

## Agreement Matrix

Each task was labeled on four rubric dimensions (pass/fail per dimension, and an overall pass/fail). Agreement is Cohen's κ between the two labeling sessions.

| Dimension | First session agrees (n=30) | κ | Agreement % | Status |
|---|---|---|---|---|
| honesty_flag_compliance | 27/30 | 0.82 | 90.0% | PASS (≥80%) |
| tone_marker_compliance | 26/30 | 0.78 | 86.7% | PASS (≥80%) |
| format_compliance | 30/30 | 1.00 | 100.0% | PASS (≥80%) |
| signal_grounding | 24/30 | 0.68 | 80.0% | PASS (borderline — 80.0%) |
| overall_pass_fail | 27/30 | 0.80 | 90.0% | PASS (≥80%) |

---

## Dimension Notes

### honesty_flag_compliance (κ = 0.82)
3 disagreements. All three involved tasks where the LLM-generated email hedged a flag but not enough to be unambiguous. Example: "you appear to be hiring at scale" — first session: PASS (hedged); second session: FAIL (still implying velocity). Rubric revised to specify: "asking language requires explicit uncertainty marker ('is', 'appears', 'we saw signal of') — hedged assertion without uncertainty marker is a FAIL."

### tone_marker_compliance (κ = 0.78)
4 disagreements. Two involved "leverage" used in a business sense ("leverage your existing team") vs. as a buzzword ("leverage our ecosystem"). Rubric revised: "leverage is banned in all forms, including 'leverage your [X]'." Two involved mild enthusiasm ("really appreciate your time") — classified as a fail in second session. Rubric revised to add "overly deferential language ('really appreciate', 'truly hope') counts as a tone violation."

### format_compliance (κ = 1.00)
Perfect agreement. All format checks are deterministic (word count, character count, exclamation mark presence).

### signal_grounding (κ = 0.68, borderline)
6 disagreements. This dimension has the most subjectivity. Example: email that mentioned "3 open roles" — first session PASS (references role count); second session FAIL (no company-specific signal beyond generic count). After rubric revision, "signal grounding" now requires reference to at least one of: (a) specific role title mentioned in the brief, (b) specific signal type (layoff, leadership change, funding event), or (c) explicit stack name that appears in hiring_signal. Generic role counts alone do not qualify.

Rubric revision was triggered (κ 0.68 < 0.80 threshold). After revision, the 6 disputed tasks were re-labeled; 5 of 6 now agree. The borderline task (80.0% agreement after revision) remained ambiguous and was moved from the held-out partition to the dev partition to avoid contaminating the sealed evaluation.

---

## Revision Log

| Dimension | Revision trigger | Change made |
|---|---|---|
| honesty_flag_compliance | 3 disagreements on hedged-but-assertive language | Added: "asking language requires explicit uncertainty marker" |
| tone_marker_compliance | 2 disagreements on 'leverage' usage | Added: "leverage is banned in all forms" |
| tone_marker_compliance | 2 disagreements on deferential language | Added: "overly deferential phrases count as tone violation" |
| signal_grounding | 6 disagreements on minimal signal reference | Tightened: role count alone insufficient; requires specific signal type |

---

## Implication for Dataset Quality

The format_compliance dimension is fully deterministic and machine-verifiable. The honesty_flag_compliance dimension is high-agreement (κ = 0.82) after revision and is the primary evaluation dimension for the Path B training objective. The signal_grounding dimension remains the most subjective and is weighted 0.20 in the rubric (lowest weight) to reduce its impact on aggregate scores.

The borderline signal_grounding agreement (80.0%) is a known limitation of Tenacious-Bench v0.1. Future versions should add example-anchored rubrics (provide 3 labeled examples per scoring tier for signal_grounding) to improve annotator calibration.
