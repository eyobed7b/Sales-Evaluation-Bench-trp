# Synthesis Memo: SimPO — Simple Preference Optimization with a Reference-Free Reward

**Paper:** Meng, Y., Xia, M., & Chen, D. (2024). *SimPO: Simple Preference Optimization with a Reference-Free Reward.* NeurIPS 2024.  
**Author:** Eyobed Feleke  
**Date:** 2026-05-01  
**Memo version:** v1

---

## Summary (one paragraph)

SimPO proposes replacing DPO's reference model log-probability ratio with a simpler, reference-free reward: the average log-probability of the completion normalized by its length, minus a target margin γ. This eliminates the need to hold a frozen reference model in memory at training time. The paper evaluates SimPO on AlpacaEval 2, MT-Bench, and Arena-Hard, finding it consistently outperforms DPO, IPO, and CPO on instruction-following benchmarks while using 10–40% less GPU memory. The length normalization component is presented as the key innovation — it prevents the model from learning to produce shorter outputs regardless of quality, a known failure mode in vanilla DPO.

---

## Specific Design Choice Where I Disagree

**SimPO recommends γ (target margin) between 0.5 and 1.5 for most tasks.** The paper's reported experiments use γ=0.7 as a default, citing optimal performance on open-ended generation benchmarks (AlpacaEval 2, Arena-Hard).

**My choice: γ=0.5.** The Tenacious judge task is a binary compliance classification task, not an open-ended generation task. The "preferred" output (correct FAIL verdict with specific violation) is already strongly differentiated from the "rejected" output (incorrect PASS) — the margin between them is qualitative, not stylistic. Using γ=0.7 or higher would push the judge to produce increasingly verbose FAIL verdicts to maximize the reward margin. At γ=0.5, the judge learns to distinguish correct from incorrect verdicts without over-committing to a specific explanation length. The judge's downstream use (rejection-sampling, not human reading) makes explanation length a secondary concern.

**Where SimPO is right:** The length normalization reward is essential. Without it (vanilla DPO), the judge would learn that the rejected output ("PASS. Score: 0.80. The email is professionally written...") is shorter than the chosen FAIL output with its detailed violation explanation — and would optimize toward shorter outputs, collapsing toward single-token verdicts.

---

## Application to Tenacious-Bench Path B

1. **Reference-free is non-negotiable at Colab T4 scale.** DPO requires a frozen reference model copy alongside the training model. At Qwen 3.5 0.8B with 4-bit quantization, a second model copy would exceed T4 VRAM. SimPO's reference-free design makes training feasible on the free tier.

2. **Binary preference structure is ideal for SimPO.** SimPO performs best when the chosen/rejected pair has clear semantic differentiation (the paper's Table 4 shows larger gains on factual tasks vs. stylistic tasks). The Tenacious judge task has the clearest possible differentiation: "this email violates a named constraint" vs. "this email is fine."

3. **Limitation I note:** SimPO's length normalization assumes the preferred completion is not systematically shorter than the rejected one. In the Tenacious training data, the chosen FAIL outputs are on average ~40 tokens longer than the rejected PASS outputs (because FAIL verdicts include violation explanations). This means length normalization is working in the intended direction — penalizing the shorter-but-incorrect PASS verdict.

4. **Generalization concern:** The training data has 84 FAIL pairs and 53 PASS pairs (imbalanced). SimPO does not natively handle class imbalance. In the next iteration (v0.2), I would oversample PASS pairs or apply a class weight to the loss to ensure the judge is not biased toward FAIL verdicts.
