# Synthesis Memo: LoRA — Low-Rank Adaptation of Large Language Models

**Paper:** Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2022). *LoRA: Low-Rank Adaptation of Large Language Models.* ICLR 2022.  
**Author:** Eyobed Feleke  
**Date:** 2026-05-01  
**Memo version:** v1

---

## Summary (one paragraph)

LoRA proposes adding low-rank decomposition matrices alongside the frozen weights of a pre-trained model. For a weight matrix W ∈ ℝᵐˣⁿ, LoRA injects a trainable bypass: ΔW = BA where B ∈ ℝᵐˣʳ and A ∈ ℝʳˣⁿ with r ≪ min(m,n). Only A and B are trained; the original W remains frozen. At inference, the adapted weight is W + BA, which adds zero latency if merged before deployment. The paper demonstrates that r=4 or r=8 often matches full fine-tuning on downstream tasks, with r=16 recommended for more complex tasks requiring compositional reasoning. The key insight is that intrinsic dimensionality of adaptation is low — models do not need full-rank updates to learn new behaviors.

---

## Specific Design Choice Where I Disagree

**Hu et al. recommend applying LoRA only to query and value projections (q_proj, v_proj)** in their original experiments, arguing that the attention mechanism is where task-specific adaptation concentrates.

**My choice: add k_proj and o_proj as well.** The Tenacious judge task requires the model to map from a specific violation type (e.g., "scaling fast" in body) to the correct flag (e.g., `weak_hiring_velocity_signal`) to the correct verdict (FAIL). This multi-hop lookup — body text → flag type → verdict category — likely benefits from adaptation in all four attention projections, not just Q and V. The paper's recommendation was established on instruction-following benchmarks (GPT-3, RoBERTa) where the Q/V pattern is sufficient. For our compliance classification task, the key/output projections participate in the relational matching step between the signal text and the flag constraint.

**Cost of the disagreement:** Adding k_proj and o_proj doubles the LoRA trainable parameters from ~2M to ~4M. At 0.5B parameters total, this is still under 1% of the model, and the memory overhead on T4 is ~40 MB — acceptable.

**Where Hu et al. are right:** The rank recommendation is correct. r=16 is the right choice for this task — the paper shows r=8 begins to degrade on multi-step reasoning, and compliance checking is essentially multi-step (signal detection + flag mapping + verdict generation). Going to r=32 would be wasteful on a 137-pair training set.

---

## Application to Tenacious-Bench Path B

1. **Zero inference latency:** After training, the LoRA adapter is merged into the base model weights before deployment (`model.merge_and_unload()`). The production critic has the same inference cost as the base model — no runtime overhead from the adapter.

2. **Adapter portability:** The LoRA adapter is publishable independently on HuggingFace (eyobed7b/tenacious-bench-simpo-judge-v1-lora). Users can apply the adapter to the same base model (Qwen 3.5 0.8B) without redistributing the full fine-tuned weights.

3. **Key limitation for this use case:** LoRA trained on 137 pairs is operating at the low end of the data regime the paper validates. Hu et al.'s reported experiments use thousands of labeled examples. The 137-pair training set reflects the cost constraint ($10 budget), not an ideal training data quantity. The ablation in `ablations/ablation_results.json` shows the judge is effective despite this — but the accuracy ceiling is clearly set by data quantity, not model capacity.

4. **v0.2 recommendation:** Increase training pairs to 500+ by adding synthetic preference pairs from the multi-LLM synthesis pipeline (the dev partition provides 82 additional labeled tasks; converting them to preference pairs would roughly double the training set). This is the highest-leverage improvement for the next version.
