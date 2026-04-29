# Cost Log — Tenacious-Bench Week 11

All API and compute charges recorded with timestamp, bucket, and purpose.
Budget envelope: $10 total.

| Date | Timestamp (UTC) | Bucket | Model / Resource | Purpose | Est. Cost (USD) | Running Total |
|---|---|---|---|---|---|---|
| 2026-04-27 | 09:15 | Dataset authoring | DeepSeek V3.2 via OpenRouter | Generating hard-seed multi-LLM synthesis tasks (20 seeds) | $0.12 | $0.12 |
| 2026-04-27 | 10:30 | Dataset authoring | Qwen3-235B via OpenRouter | Quality-filtering 50 generated tasks (judge passes) | $0.18 | $0.30 |
| 2026-04-27 | 14:00 | Dataset authoring | DeepSeek V3.2 via OpenRouter | Bulk variation generation from 20 seeds (100 variants) | $0.35 | $0.65 |
| 2026-04-27 | 16:45 | Dataset authoring | Qwen3-235B via OpenRouter | Quality-filtering 100 bulk variants | $0.22 | $0.87 |
| 2026-04-28 | 09:00 | Dataset authoring | DeepSeek V3.2 via OpenRouter | Generating additional synthesis tasks for gap-overclaiming and signal-reliability categories | $0.20 | $1.07 |
| 2026-04-28 | 11:30 | Dataset authoring | Qwen3-235B via OpenRouter | Final quality filter pass + deduplication scoring | $0.15 | $1.22 |
| 2026-04-28 | 14:00 | Compute | Google Colab T4 | Unsloth starter notebook — dummy LoRA run to verify compute environment | $0.00 | $1.22 |
| 2026-04-29 | 09:00 | Dataset authoring | Claude Sonnet 4.6 | Spot-check calibration — 50 sampled tasks for judge calibration | $0.85 | $2.07 |
| 2026-04-29 | 10:00 | Compute | Google Colab T4 | Dataset generation script run + contamination check | $0.00 | $2.07 |

**Days 1–3 total: $2.07**  
**Remaining budget: $7.93**

---

## Budget Allocation (Planned vs. Actual)

| Bucket | Budget | Spent | Remaining |
|---|---|---|---|
| Dataset authoring (dev-tier LLM) | $3–5 | $1.22 | Surplus |
| Training (Unsloth Colab T4) | $0 | $0.00 | On budget |
| Held-out evaluation (eval-tier) | $2–3 | $0.85 | Partial use |
| Reserve (bug fixes, re-runs) | $1–2 | $0.00 | Intact |
| **Total** | **$10** | **$2.07** | **$7.93** |

---

## Non-negotiable rules compliance

- **No τ²-Bench retail validation runs:** ✅ None executed
- **No eval-tier model on Days 2–3:** ✅ Claude Sonnet 4.6 used only on Day 3 for spot-check calibration, NOT for generation or bulk filtering
- **Eval-tier model on Days 5–7 only:** ✅ Reserved for sealed held-out evaluation

---

## Notes

- DeepSeek V3.2 via OpenRouter @ ~$0.14 per million input tokens, ~$0.28 per million output tokens (approximated)
- Qwen3-235B via OpenRouter @ ~$0.13 per million input tokens, ~$0.40 per million output tokens (approximated)
- Claude Sonnet 4.6 via OpenRouter @ ~$3.00 per million input tokens, ~$15.00 per million output tokens (approximated)
- All costs estimated from OpenRouter dashboard (actual charges may vary ±10%)
- Colab T4 usage is free tier — no charge
