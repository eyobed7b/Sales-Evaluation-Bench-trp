# Audit Memo: What τ²-Bench Retail Misses for Tenacious-Style B2B Sales Work

**Author:** Eyobed Feleke  
**Date:** 2026-04-29  
**Word count:** ~600  
**Probe references:** P-01, P-02, P-03, P-06, P-08, P-15, P-16, P-23, P-24  
**Trace references:** cf06a98e, 8072eb4a, 4e53f66e, 3ed10255, 5fc051b8

---

## The Gap

τ²-Bench retail measures whether a voice or text agent can complete transactional retail tasks — product lookup, order status, return initiation. Its tasks are graded on task-completion binary: did the agent resolve the customer's stated need? This framing is appropriate for retail but structurally misses the failure modes that matter for Tenacious's B2B outbound sales workflow.

Tenacious's agent does not complete a task in one turn. It constructs a signal brief from enriched prospect data, classifies the prospect into one of four ICP segments, and composes a cold outreach email that must simultaneously be honest about data confidence, grounded in verified signals, and compliant with a five-marker tone framework. No τ²-Bench task requires an agent to hold and enforce a set of honesty constraints during generation. No τ²-Bench task penalizes an agent for asserting a fact it cannot verify. No τ²-Bench task measures whether the agent correctly routes a disqualified prospect away from outreach.

## What the Week 10 Evidence Proves

**Failure mode 1: Honesty flag bypass (P-01, P-02, P-03, P-06).** The outreach composer receives honesty flags such as `weak_hiring_velocity_signal` and `tech_stack_inferred_not_confirmed` in the user prompt. Traces cf06a98e and 8072eb4a show that the model reads the hiring signal narrative text and infers velocity from it, producing phrases like "scaling fast" and "aggressively hiring" despite the flag explicitly prohibiting this. Trace 8072eb4a is a `passed: false` entry; the failure mode is the agent asserting velocity from a brief with `total_open_roles = 3` — below the five-role threshold set in `signal_brief.py:51`. τ²-Bench would score this task as passed if the agent produced any coherent reply. Tenacious-Bench scores it as failed because the reply violates an honesty constraint.

**Failure mode 2: Disqualification bypass (P-08, P-15).** The `disqualified` field is hardcoded to `False` on every code path in `icp_classifier.py` (lines 119 and 136). This means every disqualifying filter — anti-offshore founder, competitor client, interim leader, 40%+ layoff — is dead code. Traces 4e53f66e and 3ed10255 are `passed: false` entries where the agent sent outreach to companies that should have been disqualified under `seed/icp_definition.md`. τ²-Bench has no concept of a disqualification gate; it cannot measure whether the agent correctly suppressed outreach.

**Failure mode 3: Post-generation validation absence (P-16).** There is no second-pass check after the LLM generates the email. Probe P-16 confirms that `honesty_flags_applied` is a self-report from the same model that may have violated the flags. The field is populated by whatever the LLM includes in its JSON output, making it an unverified attestation. Trace 5fc051b8 is a `passed: false` entry where the LLM simultaneously reported compliance and violated the `layoff_overrides_funding` constraint by leading with funding framing.

**Failure mode 4: Tone drift (P-23, P-24).** τ²-Bench does not penalize retail agents for exclamation marks or buzzwords; those are not failure modes in retail contexts. For Tenacious, they are. Probe P-23 documents the exclamation mark injection pattern; P-24 documents buzzword injection. These are LLM behavioral failures that require a benchmark with Tenacious-specific tone markers to detect.

## Schema Consequence

These four failure modes drive the Tenacious-Bench v0.1 schema dimensions. Every task tests one of: honesty flag compliance, disqualification routing, post-generation constraint integrity, or tone marker adherence. The scoring rubric is machine-verifiable: regex checks for banned phrases, field-presence checks for disqualification routing, and an LLM judge call (a different model family from the generator) for semantic tone compliance. A generic τ²-Bench-tuned agent will fail most tasks in the honesty-flag and disqualification dimensions because those concepts do not exist in retail task structure. That is the benchmark's validity claim.
