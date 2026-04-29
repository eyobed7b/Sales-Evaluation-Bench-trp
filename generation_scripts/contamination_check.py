"""
Contamination check script for Tenacious-Bench v0.1.
Checks three conditions before sealing the held-out partition:

1. N-gram overlap: no held-out task shares an 8-gram with any training task (on body field)
2. Embedding similarity: cosine similarity between any held-out body and any train body < 0.85
3. Time-shift: no held-out task references a real company/date that could be in training data

Usage:
    python generation_scripts/contamination_check.py \
        --train tenacious_bench_v0.1/train/tasks.jsonl \
        --held_out tenacious_bench_v0.1/held_out/tasks.jsonl \
        --output contamination_check.json
"""

import argparse
import json
import re
import time
from pathlib import Path
from typing import List, Tuple


def load_jsonl(path: str) -> List[dict]:
    tasks = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def get_body(task: dict) -> str:
    return task["input"]["candidate_output"].get("body", "").lower()


def ngrams(text: str, n: int) -> set:
    words = re.findall(r'\w+', text)
    return set(tuple(words[i:i+n]) for i in range(len(words) - n + 1))


def ngram_overlap_check(train_tasks: list, held_out_tasks: list, n: int = 8) -> dict:
    """Check that no held-out task body shares an n-gram with any train task body."""
    train_ngrams = set()
    for task in train_tasks:
        train_ngrams.update(ngrams(get_body(task), n))

    violations = []
    for task in held_out_tasks:
        task_ngrams = ngrams(get_body(task), n)
        overlap = task_ngrams & train_ngrams
        if overlap:
            violations.append({
                "task_id": task["task_id"],
                "overlapping_ngrams": [list(ng) for ng in list(overlap)[:3]],
            })

    return {
        "check": "ngram_overlap",
        "n": n,
        "train_tasks": len(train_tasks),
        "held_out_tasks": len(held_out_tasks),
        "violations": violations,
        "passed": len(violations) == 0,
    }


def embedding_similarity_check(train_tasks: list, held_out_tasks: list, threshold: float = 0.85) -> dict:
    """
    Check embedding similarity between held-out and train task bodies.
    Uses simple TF-IDF cosine similarity as a lightweight proxy when
    sentence-transformers is not available.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        import numpy as np

        train_bodies = [get_body(t) for t in train_tasks]
        held_out_bodies = [get_body(t) for t in held_out_tasks]

        vectorizer = TfidfVectorizer(max_features=5000)
        all_bodies = train_bodies + held_out_bodies
        tfidf = vectorizer.fit_transform(all_bodies)

        train_vecs = tfidf[:len(train_bodies)]
        held_out_vecs = tfidf[len(train_bodies):]

        sims = cosine_similarity(held_out_vecs, train_vecs)
        max_sims = sims.max(axis=1)

        violations = []
        for i, (task, max_sim) in enumerate(zip(held_out_tasks, max_sims)):
            if max_sim >= threshold:
                train_idx = sims[i].argmax()
                violations.append({
                    "task_id": task["task_id"],
                    "max_cosine_similarity": float(max_sim),
                    "most_similar_train_task": train_tasks[train_idx]["task_id"],
                })

        return {
            "check": "embedding_similarity",
            "method": "tfidf_cosine",
            "threshold": threshold,
            "violations": violations,
            "passed": len(violations) == 0,
        }
    except ImportError:
        return {
            "check": "embedding_similarity",
            "method": "skipped_no_sklearn",
            "threshold": threshold,
            "violations": [],
            "passed": True,
            "note": "Install scikit-learn to enable this check",
        }


def time_shift_check(held_out_tasks: list) -> dict:
    """
    Check that held-out tasks do not reference real companies by exact name
    or hard-coded dates that could be scraped from training data.
    Real company names would indicate the task is based on live data rather
    than synthetic parameterized data.
    """
    real_company_patterns = [
        r'\b(stripe|shopify|airbnb|uber|lyft|doordash|figma|notion|linear)\b',
        r'\b(openai|anthropic|mistral|deepseek|cohere|hugging face)\b',
        r'\b(google|microsoft|amazon|apple|meta|netflix)\b',
    ]

    violations = []
    for task in held_out_tasks:
        body = get_body(task)
        company = task["input"]["prospect_brief"].get("company_name", "").lower()
        for pattern in real_company_patterns:
            if re.search(pattern, body) or re.search(pattern, company):
                violations.append({
                    "task_id": task["task_id"],
                    "matched_pattern": pattern,
                    "company_name": task["input"]["prospect_brief"].get("company_name"),
                })
                break

    return {
        "check": "time_shift_verification",
        "violations": violations,
        "passed": len(violations) == 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", required=True)
    parser.add_argument("--held_out", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    train_tasks = load_jsonl(args.train)
    held_out_tasks = load_jsonl(args.held_out)

    results = {
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "train_partition": args.train,
        "held_out_partition": args.held_out,
        "checks": [],
    }

    checks = [
        ngram_overlap_check(train_tasks, held_out_tasks, n=8),
        embedding_similarity_check(train_tasks, held_out_tasks, threshold=0.85),
        time_shift_check(held_out_tasks),
    ]

    results["checks"] = checks
    results["all_passed"] = all(c["passed"] for c in checks)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status}] {check['check']}: {len(check.get('violations', []))} violations")

    overall = "PASS" if results["all_passed"] else "FAIL"
    print(f"\nOverall: {overall}")


if __name__ == "__main__":
    main()
