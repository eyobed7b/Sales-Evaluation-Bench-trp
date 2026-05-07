"""
Tenacious-Bench v0.1 Scoring Evaluator
Machine-verifiable scoring for B2B sales agent evaluation tasks.

Usage:
    python scoring_evaluator.py --task task.json --output output.json
    python scoring_evaluator.py --batch tenacious_bench_v0.1/dev/ --output results.json

Requires: OPENROUTER_API_KEY in environment for llm_judge dimensions.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

SEED = 42

# Judge model — must be a different family from the generator (DeepSeek)
# to avoid preference leakage (Li et al., 2025)
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "qwen/qwen3-235b-a22b")
OPENROUTER_BASE = "https://openrouter.ai/api/v1"

JUDGE_SYSTEM_PROMPT = """You are a compliance reviewer for B2B outbound sales emails.
You will receive an email draft, context about the prospect, and a specific rubric dimension to evaluate.
Return ONLY valid JSON: {"pass": true/false, "score": 0.0-1.0, "reason": "one sentence"}

Score 1.0 = fully compliant, 0.0 = clear violation, 0.5 = partial/ambiguous.
Be strict. A "soft" buzzword or mildly assertive claim should score 0.5, not 1.0.
"""


def _regex_check(body: str, subject: str, dimension: dict) -> dict:
    """Check regex banned/required patterns against subject+body."""
    full_text = (subject + " " + body).lower()
    violations = []
    missing = []

    for pattern in dimension.get("banned_patterns", []):
        if re.search(pattern.lower(), full_text):
            violations.append(pattern)

    for pattern in dimension.get("required_patterns", []):
        if not re.search(pattern.lower(), full_text):
            missing.append(pattern)

    passed = (len(violations) == 0) and (len(missing) == 0)
    if violations:
        reason = f"Banned pattern(s) found: {violations}"
        score = 0.0
    elif missing:
        reason = f"Required pattern(s) missing: {missing}"
        score = 0.0
    else:
        reason = "All regex checks passed"
        score = 1.0

    return {"pass": passed, "score": score, "reason": reason}


def _length_check(body: str, subject: str, dimension: dict) -> dict:
    """Check word count, subject character length, subject prefix, and exclamation marks."""
    violations = []

    word_count = len(body.split())
    max_words = dimension.get("max_value", 120)
    if word_count > max_words:
        violations.append(f"Body word count {word_count} exceeds max {max_words}")

    subject_len = len(subject)
    if subject_len > 60:
        violations.append(f"Subject length {subject_len} chars exceeds max 60")

    if re.search(r"!", subject + body):
        violations.append("Exclamation mark(s) present")

    # Style Guide v2: subject must start with canonical prefix
    allowed_prefixes = ("request:", "follow-up:", "context:", "question:")
    subject_lower = subject.strip().lower()
    if subject_lower and not any(subject_lower.startswith(p) for p in allowed_prefixes):
        violations.append(
            f"Subject must start with Request/Follow-up/Context/Question (got: '{subject[:40]}')"
        )

    passed = len(violations) == 0
    score = 1.0 if passed else max(0.0, 1.0 - 0.25 * len(violations))
    reason = "; ".join(violations) if violations else "All length/format checks passed"
    return {"pass": passed, "score": score, "reason": reason}


def _field_presence_check(candidate_output: dict, dimension: dict) -> dict:
    """Check that required fields are present and non-empty."""
    required = dimension.get("required_fields", [])
    missing = [f for f in required if not candidate_output.get(f)]
    passed = len(missing) == 0
    return {
        "pass": passed,
        "score": 1.0 if passed else 0.0,
        "reason": f"Missing fields: {missing}" if missing else "All required fields present",
    }


def _llm_judge(
    body: str,
    subject: str,
    prospect_brief: dict,
    dimension: dict,
    api_key: Optional[str] = None,
) -> dict:
    """Call LLM judge for semantic evaluation. Falls back to heuristic if no API key."""
    if not api_key:
        return {
            "pass": None,
            "score": None,
            "reason": "LLM judge skipped — set OPENROUTER_API_KEY to enable",
        }

    try:
        import urllib.request

        user_content = f"""RUBRIC DIMENSION: {dimension['name']}
PASS CONDITION: {dimension['pass_condition']}
FAIL CONDITION: {dimension['fail_condition']}

PROSPECT CONTEXT:
- Company: {prospect_brief.get('company_name')}
- Segment: {prospect_brief.get('segment')}
- Honesty flags: {prospect_brief.get('honesty_flags')}
- Hiring signal: {prospect_brief.get('hiring_signal', '')}[:200]
- Leadership signal: {prospect_brief.get('leadership_signal', 'None')}

EMAIL:
Subject: {subject}
Body: {body}

Evaluate whether this email passes the rubric dimension above. Return JSON only."""

        payload = json.dumps({
            "model": JUDGE_MODEL,
            "messages": [
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            "temperature": 0.0,
            "max_tokens": 150,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{OPENROUTER_BASE}/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/eyobed7b/tenacious-bench",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            content = result["choices"][0]["message"]["content"]
            # Strip markdown code fences if present
            content = re.sub(r"```json\s*|\s*```", "", content.strip())
            return json.loads(content)

    except Exception as e:
        return {"pass": None, "score": None, "reason": f"LLM judge error: {e}"}


def score_dimension(
    dimension: dict,
    body: str,
    subject: str,
    candidate_output: dict,
    prospect_brief: dict,
    api_key: Optional[str] = None,
) -> dict:
    """Score a single rubric dimension. Returns {pass, score, reason, weight}."""
    verifier = dimension["verifier_type"]
    weight = dimension["weight"]

    if verifier == "regex":
        result = _regex_check(body, subject, dimension)
    elif verifier == "length_check":
        result = _length_check(body, subject, dimension)
    elif verifier == "field_presence":
        result = _field_presence_check(candidate_output, dimension)
    elif verifier == "llm_judge":
        result = _llm_judge(body, subject, prospect_brief, dimension, api_key)
    else:
        result = {"pass": None, "score": None, "reason": f"Unknown verifier: {verifier}"}

    return {**result, "dimension": dimension["name"], "weight": weight}


def score_task(task: dict, api_key: Optional[str] = None) -> dict:
    """
    Score a single task. Returns full scoring trace with per-dimension results
    and a weighted aggregate score.
    """
    task_id = task["task_id"]
    candidate = task["input"]["candidate_output"]
    brief = task["input"]["prospect_brief"]
    body = candidate.get("body", "")
    subject = candidate.get("subject", "")
    dimensions = task["scoring_rubric"]["dimensions"]

    dim_results = []
    weighted_sum = 0.0
    total_weight = 0.0

    for dim in dimensions:
        result = score_dimension(dim, body, subject, candidate, brief, api_key)
        dim_results.append(result)
        if result["score"] is not None:
            weighted_sum += result["score"] * result["weight"]
            total_weight += result["weight"]

    aggregate_score = weighted_sum / total_weight if total_weight > 0 else None
    passed = (aggregate_score is not None) and (aggregate_score >= 0.7)

    ground_truth = task.get("ground_truth", {})
    expected_pass = ground_truth.get("expected_pass")
    expected_score = ground_truth.get("expected_score")

    correct_classification = None
    if expected_pass is not None and aggregate_score is not None:
        correct_classification = (passed == expected_pass)

    score_delta = None
    if expected_score is not None and aggregate_score is not None:
        score_delta = abs(aggregate_score - expected_score)

    return {
        "task_id": task_id,
        "failure_category": task.get("failure_category"),
        "difficulty": task.get("difficulty"),
        "source_mode": task.get("source_mode"),
        "aggregate_score": round(aggregate_score, 4) if aggregate_score is not None else None,
        "passed": passed,
        "expected_pass": expected_pass,
        "expected_score": expected_score,
        "correct_classification": correct_classification,
        "score_delta": round(score_delta, 4) if score_delta is not None else None,
        "dimension_results": dim_results,
        "scored_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "judge_model": JUDGE_MODEL,
        "seed": SEED,
    }


def score_batch(task_dir: str, api_key: Optional[str] = None) -> list:
    """Score all .jsonl or .json tasks in a directory."""
    results = []
    path = Path(task_dir)
    files = sorted(list(path.glob("*.jsonl")) + list(path.glob("*.json")))

    for f in files:
        if f.name.startswith("."):
            continue
        try:
            with open(f) as fh:
                content = fh.read().strip()
            # Support both JSON array and JSONL
            if content.startswith("["):
                tasks = json.loads(content)
            else:
                tasks = [json.loads(line) for line in content.splitlines() if line.strip()]
            for task in tasks:
                result = score_task(task, api_key)
                results.append(result)
        except Exception as e:
            print(f"Error scoring {f}: {e}", file=sys.stderr)

    return results


def summary_stats(results: list) -> dict:
    """Compute aggregate statistics over a batch of scored tasks."""
    valid = [r for r in results if r["aggregate_score"] is not None]
    if not valid:
        return {"error": "no valid results"}

    scores = [r["aggregate_score"] for r in valid]
    pass_rate = sum(1 for r in valid if r["passed"]) / len(valid)
    correct = [r for r in valid if r.get("correct_classification") is True]
    accuracy = len(correct) / len(valid) if valid else 0.0

    by_category = {}
    for r in valid:
        cat = r.get("failure_category", "unknown")
        by_category.setdefault(cat, []).append(r["aggregate_score"])

    category_means = {k: round(sum(v) / len(v), 4) for k, v in by_category.items()}

    # False PASS rate on expected_fail tasks — primary diagnostic for PASS bias.
    # A high false_pass_rate on disqualification categories indicates β is too low
    # or the SimPO target margin is missing. Run this before any retraining.
    expected_fail = [r for r in valid if r.get("expected_pass") is False]
    false_pass_rate = None
    if expected_fail:
        false_passes = sum(1 for r in expected_fail if r.get("passed") is True)
        false_pass_rate = round(false_passes / len(expected_fail), 4)

    # Per-category recall on expected_fail tasks — identifies which categories
    # drive PASS bias. Compare icp-misclassification recall against other categories.
    category_recall = {}
    by_cat_fail = {}
    for r in valid:
        if r.get("expected_pass") is False:
            cat = r.get("failure_category", "unknown")
            by_cat_fail.setdefault(cat, {"total": 0, "correct_fail": 0})
            by_cat_fail[cat]["total"] += 1
            if r.get("correct_classification") is True:
                by_cat_fail[cat]["correct_fail"] += 1
    for cat, counts in by_cat_fail.items():
        if counts["total"] > 0:
            category_recall[cat] = round(counts["correct_fail"] / counts["total"], 4)

    return {
        "n_tasks": len(valid),
        "mean_score": round(sum(scores) / len(scores), 4),
        "pass_rate": round(pass_rate, 4),
        "classification_accuracy": round(accuracy, 4),
        "category_mean_scores": category_means,
        "false_pass_rate_on_expected_fail": false_pass_rate,
        "category_recall_on_expected_fail": category_recall,
    }


def main():
    parser = argparse.ArgumentParser(description="Tenacious-Bench v0.1 Scoring Evaluator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--task", help="Path to single task JSON file")
    group.add_argument("--batch", help="Path to directory of task files")
    parser.add_argument("--output", required=True, help="Output JSON file for results")
    parser.add_argument("--no-llm", action="store_true", help="Skip LLM judge dimensions")
    args = parser.parse_args()

    api_key = None if args.no_llm else os.getenv("OPENROUTER_API_KEY")

    if args.task:
        with open(args.task) as f:
            task = json.load(f)
        result = score_task(task, api_key)
        output = {"results": [result], "summary": summary_stats([result])}
    else:
        results = score_batch(args.batch, api_key)
        output = {"results": results, "summary": summary_stats(results)}

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    stats = output["summary"]
    print(f"Scored {stats.get('n_tasks', 0)} tasks")
    print(f"Mean score:   {stats.get('mean_score')}")
    print(f"Pass rate:    {stats.get('pass_rate')}")
    print(f"Accuracy:     {stats.get('classification_accuracy')}")


if __name__ == "__main__":
    main()
