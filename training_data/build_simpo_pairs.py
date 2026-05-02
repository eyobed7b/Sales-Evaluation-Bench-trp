"""
Build SimPO preference pairs from the Tenacious-Bench training partition.

Each pair:
  prompt   = judge context (prospect brief + candidate email + rubric description)
  chosen   = correct compliance verdict (honest assessment)
  rejected = plausible incorrect verdict (untrained model's over-generous response)

Format follows the HuggingFace TRL SimPO trainer expected input.
Run from repo root:
    python training_data/build_simpo_pairs.py
"""

import json
import random
from pathlib import Path

SEED = 42
random.seed(SEED)


def _format_brief(brief: dict) -> str:
    lines = [
        f"Company: {brief['company_name']}",
        f"Segment: {brief['segment']}",
        f"Honesty flags: {', '.join(brief['honesty_flags'])}",
        f"Hiring signal: {brief['hiring_signal']}",
        f"AI maturity: {brief['ai_maturity_signal']}",
    ]
    if brief.get("layoff_signal"):
        lines.append(f"Layoff signal: {brief['layoff_signal']}")
    if brief.get("leadership_signal"):
        lines.append(f"Leadership signal: {brief['leadership_signal']}")
    return "\n".join(lines)


def _format_rubric_summary(task: dict) -> str:
    dims = task["scoring_rubric"]["dimensions"]
    parts = []
    for d in dims:
        parts.append(
            f"- {d['name']} (w={d['weight']}): PASS if {d['pass_condition']}; "
            f"FAIL if {d['fail_condition']}"
        )
    return "\n".join(parts)


def _make_prompt(task: dict) -> str:
    brief = task["input"]["prospect_brief"]
    out = task["input"]["candidate_output"]
    return (
        "You are a compliance reviewer for B2B outbound sales emails.\n"
        "Evaluate the following email draft against the rubric. "
        "Return a verdict (PASS or FAIL), a score (0.0–1.0), "
        "and the specific violation if any.\n\n"
        f"PROSPECT BRIEF:\n{_format_brief(brief)}\n\n"
        f"EMAIL:\nSubject: {out['subject']}\n{out['body']}\n\n"
        f"RUBRIC:\n{_format_rubric_summary(task)}"
    )


def _make_chosen_fail(task: dict) -> str:
    gt = task["ground_truth"]
    violation = gt.get("key_violation", "policy violation")
    score = gt.get("expected_score", 0.2)
    return (
        f"FAIL. Score: {score:.2f}.\n"
        f"Violation: {violation}.\n"
        f"{gt.get('explanation', 'The email violates one or more honesty constraints.')}"
    )


def _make_chosen_pass(task: dict) -> str:
    gt = task["ground_truth"]
    score = gt.get("expected_score", 0.85)
    return (
        f"PASS. Score: {score:.2f}.\n"
        f"{gt.get('explanation', 'The email correctly applies all honesty flags and tone markers.')}"
    )


def _make_rejected_for_fail(task: dict) -> str:
    """Incorrect PASS verdict for a failing email — what the untrained model says."""
    out = task["input"]["candidate_output"]
    return (
        "PASS. Score: 0.80.\n"
        "The email is professionally written and references the prospect's context. "
        "The tone is appropriate and no obvious violations are present."
    )


def _make_rejected_for_pass(task: dict) -> str:
    """Over-strict FAIL verdict for a passing email — what a miscalibrated judge says."""
    flags = task["input"]["prospect_brief"]["honesty_flags"]
    return (
        f"FAIL. Score: 0.45.\n"
        f"The email may implicitly assert claims that could conflict with active flags "
        f"({', '.join(flags)}). The claim about available engineers could be read as "
        f"overclaiming capacity. Recommend revision."
    )


def build_pairs(train_path: str) -> list:
    tasks = [json.loads(l) for l in open(train_path)]
    pairs = []

    for task in tasks:
        is_pass = task["ground_truth"]["expected_pass"]
        prompt = _make_prompt(task)

        if is_pass:
            chosen = _make_chosen_pass(task)
            rejected = _make_rejected_for_pass(task)
        else:
            chosen = _make_chosen_fail(task)
            rejected = _make_rejected_for_fail(task)

        pairs.append({
            "task_id": task["task_id"],
            "failure_category": task["failure_category"],
            "difficulty": task["difficulty"],
            "source_mode": task["source_mode"],
            "expected_pass": is_pass,
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected,
        })

    random.shuffle(pairs)
    return pairs


if __name__ == "__main__":
    pairs = build_pairs("tenacious_bench_v0.1/train/tasks.jsonl")
    out_path = Path("training_data/simpo_pairs.jsonl")
    with open(out_path, "w") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")
    print(f"Wrote {len(pairs)} preference pairs → {out_path}")
    print(f"  FAIL pairs: {sum(1 for p in pairs if not p['expected_pass'])}")
    print(f"  PASS pairs: {sum(1 for p in pairs if p['expected_pass'])}")
