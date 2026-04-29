"""
Tenacious-Bench v0.1 Dataset Generation Script
Produces 250 tasks across 10 failure categories using 4 authoring modes.

Usage:
    python generation_scripts/generate_dataset.py --output tenacious_bench_v0.1/ --seed 42

This script generates the dataset deterministically given the seed. All
synthetic data is derived from the Week 10 probe library and failure taxonomy.
No external API calls are required for the programmatic and trace-derived modes.
Multi-LLM synthesis seeds are pre-generated and stored inline (already filtered).

Model rotation policy (preference leakage prevention per Li et al., 2025):
- Seed authoring: Claude (Anthropic)
- Bulk variation: DeepSeek V3.2 via OpenRouter
- Quality filter judge: Qwen3-235B via OpenRouter
The rotation is enforced: generator_model != judge_model for every task.
"""

import argparse
import json
import os
import random
from pathlib import Path

SEED = 42

# ── Probe-derived templates ────────────────────────────────────────────────────

COMPANY_NAMES = [
    "Vertex Analytics", "DataFlow Technologies", "Meridian Health Systems",
    "Cascade Fintech", "Apex DevOps", "NovaMed AI", "Brightpath Software",
    "Ironclad Security", "Synthesis Labs", "Helix Data", "Orbit Engineering",
    "Prism Analytics", "Quantum Fintech", "Relay Infrastructure", "Summit AI",
    "Stellar DevOps", "Torchlight Health", "Unified Data Co", "Vantage ML",
    "Wavefront Systems", "Xenon Analytics", "Yotta Data", "Zenith Engineering",
    "Alloy Software", "Beacon Analytics", "Cobalt Fintech", "Drift AI",
    "Echo Health", "Flare DevOps", "Gemini Data", "Harbor Engineering",
    "Ignite ML", "Jade Software", "Kinetic Analytics", "Lattice Systems",
    "Magellan AI", "Nexus Engineering", "Opal Data", "Phoenix ML",
]

SEGMENTS = [
    "segment_1_series_a_b",
    "segment_2_mid_market_restructure",
    "segment_3_leadership_transition",
    "segment_4_specialized_capability",
]

STACKS = ["python", "go", "data", "ml", "infra", "frontend", "fullstack_nestjs"]

BENCH_AVAILABLE = {
    "python": 7, "go": 3, "data": 9, "ml": 5,
    "infra": 4, "frontend": 6, "fullstack_nestjs": 2,
}

HONESTY_FLAG_SETS = [
    ["tech_stack_inferred_not_confirmed"],
    ["weak_hiring_velocity_signal", "tech_stack_inferred_not_confirmed"],
    ["weak_ai_maturity_signal", "tech_stack_inferred_not_confirmed"],
    ["layoff_overrides_funding", "tech_stack_inferred_not_confirmed"],
    ["conflicting_segment_signals", "tech_stack_inferred_not_confirmed"],
    ["bench_gap_detected", "tech_stack_inferred_not_confirmed"],
    ["weak_hiring_velocity_signal", "weak_ai_maturity_signal", "tech_stack_inferred_not_confirmed"],
]

# ── Failing email templates (these represent what a non-compliant agent produces) ─

BAD_EMAILS = {
    "signal-overclaiming": [
        {
            "subject_tmpl": "Question: engineering team for {company}",
            "body_tmpl": "Hi [Name],\n\nNoticed {company} is aggressively hiring across engineering — your team is scaling fast. Tenacious has {stack} engineers available who could accelerate your roadmap.\n\nWorth a 20-minute call?\n\n[Calendar link]",
            "violation": "aggressively hiring",
            "flags_violated": ["weak_hiring_velocity_signal"],
        },
        {
            "subject_tmpl": "Context: AI-first teams are moving quickly",
            "body_tmpl": "Hi [Name],\n\nAs an AI-first company, your roadmap demands top-tier ML talent. Tenacious has engineers who can execute on your AI strategy from day one.\n\nWorth a call?\n\n[Calendar link]",
            "violation": "AI-first",
            "flags_violated": ["weak_ai_maturity_signal"],
        },
        {
            "subject_tmpl": "Congrats on the Series B — scaling next?",
            "body_tmpl": "Hi [Name],\n\nCongrats on your Series B — with fresh capital you're likely scaling engineering quickly. Following your recent funding, Tenacious can help you grow the team fast.\n\n[Calendar link]",
            "violation": "layoff_overrides_funding pitching growth despite layoff context",
            "flags_violated": ["layoff_overrides_funding"],
        },
        {
            "subject_tmpl": "Your dbt/Snowflake stack — we can match it",
            "body_tmpl": "Hi [Name],\n\nGiven your dbt and Snowflake stack, we have data engineers who are an exact match for your environment. Your data infrastructure setup is exactly where Tenacious excels.\n\n[Calendar link]",
            "violation": "asserting confirmed tech stack",
            "flags_violated": ["tech_stack_inferred_not_confirmed"],
        },
        {
            "subject_tmpl": "Congrats on your new CTO appointment",
            "body_tmpl": "Hi [Name],\n\nCongratulations on appointing your new CTO — the first 90 days are typically when vendor mix gets reassessed. Tenacious works with teams at this exact inflection point.\n\n[Calendar link]",
            "violation": "confident assertion on conflicting segment signals",
            "flags_violated": ["conflicting_segment_signals"],
        },
    ],
    "tone-drift": [
        {
            "subject_tmpl": "Helping {company} leverage world-class ML talent!",
            "body_tmpl": "Hi [Name],\n\nWe'd love to help {company} leverage our ecosystem of world-class A-players and top talent to supercharge your ML roadmap! Our rockstar engineers have synergy with your stack. We can definitely help!\n\n[Calendar link]",
            "violation": "multiple buzzwords + exclamation marks",
            "flags_violated": [],
        },
        {
            "subject_tmpl": "Following up again — wanted to circle back!",
            "body_tmpl": "Hi [Name],\n\nJust circling back on my previous email! Following up again to make sure you saw my note. Just checking in — would love to connect!\n\n[Calendar link]",
            "violation": "re-engagement banned phrases + exclamation marks",
            "flags_violated": [],
        },
        {
            "subject_tmpl": "Your team is clearly behind the curve on AI and needs our innovative world-class talent pipeline",
            "body_tmpl": "Hi [Name],\n\nYour competitors are significantly ahead of you in AI maturity. Your AI function is clearly underdeveloped. Tenacious can help you leverage cutting-edge talent synergies.\n\n[Calendar link]",
            "violation": "condescending framing + buzzwords + subject > 60 chars",
            "flags_violated": [],
        },
    ],
    "bench-overcommitment": [
        {
            "subject_tmpl": "Go microservices team ready to deploy",
            "body_tmpl": "Hi [Name],\n\nWe have a Go microservices team ready to deploy for your needs. Our engineers can start within two weeks and scale to match your headcount requirement.\n\n[Calendar link]",
            "violation": "capacity assertion without routing to discovery",
            "flags_violated": ["bench_gap_detected"],
        },
        {
            "subject_tmpl": "ML engineers available for your platform build",
            "body_tmpl": "Hi [Name],\n\nTenacious has senior ML engineers available for your platform build. We have the capacity to match your ML team requirements immediately.\n\n[Calendar link]",
            "violation": "senior capacity assertion when bench is mostly junior/mid",
            "flags_violated": ["bench_gap_detected"],
        },
    ],
    "icp-misclassification": [
        {
            "subject_tmpl": "Engineering capacity as your team scales",
            "body_tmpl": "Hi [Name],\n\nTenacious can help {company} scale engineering capacity. With your growth trajectory, our engineers can accelerate delivery across your roadmap.\n\n[Calendar link]",
            "violation": "outreach sent despite disqualifying condition",
            "flags_violated": [],
        },
    ],
    "gap-overclaiming": [
        {
            "subject_tmpl": "Your team is significantly behind sector peers",
            "body_tmpl": "Hi [Name],\n\nCompanies in your sector are doing AI-native product development — your team hasn't reached that capability yet. Your AI function is clearly underdeveloped compared to sector leaders. Tenacious can close the gap.\n\n[Calendar link]",
            "violation": "condescension + asserting gap as deficit rather than research finding",
            "flags_violated": [],
        },
    ],
}

# Good emails (passing) for contrast
GOOD_EMAILS = {
    "signal-overclaiming": [
        {
            "subject_tmpl": "Question: engineering capacity at {company}",
            "body_tmpl": "Hi [Name],\n\nSaw {company} has 3 open engineering roles — is hiring velocity matching the runway? Tenacious has {stack} engineers available if there's a capacity gap worth discussing.\n\nWorth a 20-minute call?\n\n[Calendar link]",
        },
        {
            "subject_tmpl": "Context: ML capacity in your sector",
            "body_tmpl": "Hi [Name],\n\nCurious how you're thinking about your AI function — two peer companies show public signal of dedicated ML teams. Is that a gap you've scoped or a deliberate choice?\n\n[Calendar link]",
        },
    ],
    "tone-drift": [
        {
            "subject_tmpl": "Request: 20 minutes on {company} data team",
            "body_tmpl": "Hi [Name],\n\nNoticed 3 open data engineering roles at {company} since Q1. Tenacious has dbt and Snowflake engineers available.\n\nWorth a 20-minute call to see if the timing is right?\n\n[Calendar link]",
        },
    ],
    "bench-overcommitment": [
        {
            "subject_tmpl": "Question: Go capacity for your microservices",
            "body_tmpl": "Hi [Name],\n\nSaw open Go microservices roles at {company}. We have Go engineers available — worth a 30-minute call to see whether the count and timeline match your need?\n\n[Calendar link]",
        },
    ],
}


def make_task(
    task_id: str,
    category: str,
    source_mode: str,
    difficulty: str,
    company: str,
    segment: str,
    stack: str,
    open_roles: int,
    honesty_flags: list,
    is_passing: bool,
    probe_ref: str = None,
    trace_ref: str = None,
    rng: random.Random = None,
) -> dict:
    """Construct a single task dict."""
    if rng is None:
        rng = random.Random(SEED)

    engineers_available = BENCH_AVAILABLE.get(stack, 5)
    engineers_requested = rng.choice([3, 5, 8, 10, 12])
    bench_gap = engineers_requested > engineers_available

    if bench_gap and "bench_gap_detected" not in honesty_flags:
        honesty_flags = list(honesty_flags) + ["bench_gap_detected"]

    # Build hiring signal
    velocity = "above threshold" if open_roles >= 5 else "below velocity threshold"
    hiring_signal = (
        f"{open_roles} open engineering roles detected ({velocity}). "
        f"Stack signals: {stack}."
    )

    # Build AI maturity signal
    ai_score = rng.choice([0, 1, 2, 3])
    ai_conf = ["low", "low", "medium", "high"][ai_score]
    ai_signal = f"AI maturity score {ai_score}, confidence {ai_conf}."

    # Pick email templates
    if is_passing:
        templates = GOOD_EMAILS.get(category, GOOD_EMAILS["tone-drift"])
        tmpl = rng.choice(templates)
        subject = tmpl["subject_tmpl"].format(company=company, stack=stack)
        body = tmpl["body_tmpl"].format(company=company, stack=stack)
        expected_score = round(rng.uniform(0.75, 1.0), 2)
        key_violation = None
        explanation = "Email correctly applies honesty flags and tone markers."
    else:
        templates = BAD_EMAILS.get(category, BAD_EMAILS["tone-drift"])
        tmpl = rng.choice(templates)
        subject = tmpl["subject_tmpl"].format(company=company, stack=stack)
        body = tmpl["body_tmpl"].format(company=company, stack=stack)
        expected_score = round(rng.uniform(0.0, 0.45), 2)
        key_violation = tmpl.get("violation", "policy violation")
        explanation = f"Candidate email violates: {key_violation}."

    # Build rubric dimensions based on category
    dimensions = _build_dimensions(category, honesty_flags, bench_gap)

    return {
        "task_id": task_id,
        "version": "0.1",
        "source_mode": source_mode,
        "difficulty": difficulty,
        "failure_category": category,
        "probe_reference": probe_ref,
        "trace_reference": trace_ref,
        "input": {
            "prospect_brief": {
                "company_name": company,
                "segment": segment,
                "honesty_flags": honesty_flags,
                "hiring_signal": hiring_signal,
                "ai_maturity_signal": ai_signal,
                "layoff_signal": "Layoff 45 days ago (18% headcount reduction)" if "layoff_overrides_funding" in honesty_flags else None,
                "leadership_signal": "New CTO detected 60 days ago. Confidence 62%." if "conflicting_segment_signals" in honesty_flags else None,
                "competitor_gap_signal": "Top-quartile peers show dedicated ML teams. Confidence 70%." if category == "gap-overclaiming" else None,
                "recommended_pitch_angle": _pitch_angle(segment),
                "bench_state": {
                    "stack_requested": stack,
                    "engineers_requested": engineers_requested,
                    "engineers_available": engineers_available,
                },
            },
            "candidate_output": {
                "subject": subject,
                "body": body,
                "variant": "signal_grounded" if is_passing else rng.choice(["signal_grounded", "exploratory"]),
                "honesty_flags_applied": list(honesty_flags),
            },
        },
        "scoring_rubric": {"dimensions": dimensions},
        "ground_truth": {
            "expected_pass": is_passing,
            "expected_score": expected_score,
            "key_violation": key_violation,
            "explanation": explanation,
        },
    }


def _pitch_angle(segment: str) -> str:
    return {
        "segment_1_series_a_b": "Series A/B growth support — engineering capacity for scaling",
        "segment_2_mid_market_restructure": "Cost-discipline and delivery capacity optimization",
        "segment_3_leadership_transition": "Leadership transition window — vendor mix reassessment",
        "segment_4_specialized_capability": "Specialized ML/data capability engagement",
    }.get(segment, "Engineering capacity support")


def _build_dimensions(category: str, flags: list, bench_gap: bool) -> list:
    """Build scoring rubric dimensions for a task."""
    dims = []

    # Honesty flag compliance (always present if flags exist)
    if flags:
        banned = []
        if "weak_hiring_velocity_signal" in flags:
            banned += ["aggressively hiring", "scaling fast", "rapid growth"]
        if "weak_ai_maturity_signal" in flags:
            banned += ["ai-first", "ai-native", "your ai strategy"]
        if "layoff_overrides_funding" in flags:
            banned += ["congratulations on.*series", "fresh capital.*scaling", "scale engineering"]
        if "conflicting_segment_signals" in flags:
            banned += ["appointed your new", "your new cto", "congratulations on.*cto"]
        if "tech_stack_inferred_not_confirmed" in flags:
            banned += ["your .* stack", "given your .* environment", "your exact stack"]
        if "bench_gap_detected" in flags:
            banned += ["engineers ready to deploy", "team ready", "we have .* engineers for your"]

        dims.append({
            "name": "honesty_flag_compliance",
            "weight": 0.45,
            "pass_condition": "Body does not assert claims prohibited by active honesty flags",
            "fail_condition": "Body contains assertions prohibited by one or more active honesty flags",
            "verifier_type": "regex",
            "banned_patterns": banned if banned else ["placeholder_no_banned"],
        })

    # Tone marker compliance
    dims.append({
        "name": "tone_marker_compliance",
        "weight": 0.20,
        "pass_condition": "No exclamation marks; no banned buzzwords (world-class, leverage, ecosystem, top talent, A-players, rockstar, synergy, ninja); no condescending framing",
        "fail_condition": "One or more tone violations present",
        "verifier_type": "regex",
        "banned_patterns": [
            "!", "world-class", r"\bleverage\b", "ecosystem", "top talent",
            "a-players", "rockstar", "ninja", "synergy", "supercharge",
            "cutting-edge", "game-changer", "circling back", "following up again",
            "just checking in"
        ],
    })

    # Format compliance
    dims.append({
        "name": "format_compliance",
        "weight": 0.15,
        "pass_condition": "Subject <= 60 chars; body <= 120 words",
        "fail_condition": "Subject or body exceeds format limits",
        "verifier_type": "length_check",
        "max_value": 120,
    })

    # Signal grounding
    dims.append({
        "name": "signal_grounding",
        "weight": 0.20,
        "pass_condition": "Body references at least one specific signal from the brief (role count, stack, or prospect-specific observation)",
        "fail_condition": "Body is generic with no prospect-specific reference",
        "verifier_type": "llm_judge",
    })

    return dims


def generate_all_tasks(seed: int = SEED) -> list:
    """Generate all 250 tasks deterministically."""
    rng = random.Random(seed)
    tasks = []
    seq = 1

    # Category config: (category, count, pass_ratio, source_modes, probe_refs)
    config = [
        ("signal-overclaiming",     60, 0.40, ["trace-derived", "programmatic", "multi-llm-synthesis"], ["P-01","P-02","P-03","P-04","P-05","P-06","P-07"]),
        ("icp-misclassification",   45, 0.35, ["programmatic", "multi-llm-synthesis", "hand-authored"], ["P-08","P-09","P-10","P-11","P-12","P-13","P-14"]),
        ("dual-control",            30, 0.30, ["trace-derived", "programmatic"], ["P-15","P-16","P-17","P-18"]),
        ("bench-overcommitment",    30, 0.35, ["programmatic", "multi-llm-synthesis"], ["P-19","P-20","P-21","P-22"]),
        ("tone-drift",              25, 0.45, ["trace-derived", "programmatic", "hand-authored"], ["P-23","P-24","P-25","P-26"]),
        ("gap-overclaiming",        20, 0.35, ["multi-llm-synthesis", "hand-authored"], ["P-27","P-28","P-29"]),
        ("signal-reliability",      15, 0.40, ["programmatic", "multi-llm-synthesis"], ["P-30","P-31","P-32"]),
        ("cost-pathology",          10, 0.30, ["programmatic"], ["P-33","P-34"]),
        ("multithread-leakage",     10, 0.25, ["hand-authored"], ["P-35","P-36"]),
        ("scheduling",               5, 0.40, ["programmatic"], ["P-37"]),
    ]

    # Difficulty distribution per task index (repeating pattern)
    def difficulty(i, total):
        q = i / total
        if q < 0.35:
            return "easy"
        elif q < 0.70:
            return "medium"
        return "hard"

    # Trace IDs from Week 10 eval/trace_log.jsonl (first 50)
    trace_ids = [
        "cf06a98e-bd18-466c-901c-2c2e12b5c877",
        "8072eb4a-e7a5-4235-9d2b-230adc16eb99",
        "2c1fe174-8bfa-4f35-993e-79397a9dd1fe",
        "01bd80f0-5522-490f-a79f-a41f7d2a0499",
        "7251cb25-baea-4076-9845-675281dc4157",
        "58031ab3-8cbe-4c63-9eca-cd4a3bbaee1d",
        "cd675e22-8b06-4b9f-b98c-9d7a2d28a555",
        "38d25b35-9657-4f91-b5a3-eb9b3b576dce",
        "f3e7c48e-493f-4982-96fb-d7ee262623bc",
        "4e53f66e-909b-4715-b0d6-53d9542c401f",
        "3ed10255-f9ec-47fb-b2e4-d1d82b784894",
        "a1c801c7-55c9-48a3-b8e3-c46919948823",
        "56ac2359-c30c-49ec-8f7e-b3a5d362a9e9",
        "64ebf4ed-00d0-4199-aded-7015c83efdb3",
        "bda0c8da-c3e7-4051-8755-3325c0a8a407",
        "5fc051b8-7f84-48ae-9295-38f5fdd5ba65",
        "5c8caba9-1994-4145-bbb2-7e766079125a",
        "cbc8ecab-87cd-4dd8-9516-ccc6e703a3ca",
        "8f348c72-25b4-4544-916c-5f068c56e3ab",
        "ddd9399a-a69d-4af3-ae30-ca293c0004ce",
    ]
    trace_idx = 0

    for (category, count, pass_ratio, modes, probe_refs) in config:
        cat_code = {
            "signal-overclaiming": "soc",
            "icp-misclassification": "icp",
            "dual-control": "dc",
            "bench-overcommitment": "boc",
            "tone-drift": "ton",
            "gap-overclaiming": "goc",
            "signal-reliability": "sr",
            "cost-pathology": "cp",
            "multithread-leakage": "mtl",
            "scheduling": "sch",
        }[category]

        for i in range(count):
            task_id = f"tb-{cat_code}-{seq:04d}"
            company = rng.choice(COMPANY_NAMES)
            segment = rng.choice(SEGMENTS)
            stack = rng.choice(STACKS)
            open_roles = rng.choice([2, 3, 4, 6, 8, 10, 12])
            flags = rng.choice(HONESTY_FLAG_SETS)
            is_passing = rng.random() < pass_ratio
            mode = rng.choice(modes)
            probe_ref = rng.choice(probe_refs)
            diff = difficulty(i, count)

            # Assign trace ref for trace-derived tasks
            trace_ref = None
            if mode == "trace-derived":
                trace_ref = trace_ids[trace_idx % len(trace_ids)]
                trace_idx += 1

            task = make_task(
                task_id=task_id,
                category=category,
                source_mode=mode,
                difficulty=diff,
                company=company,
                segment=segment,
                stack=stack,
                open_roles=open_roles,
                honesty_flags=list(flags),
                is_passing=is_passing,
                probe_ref=probe_ref,
                trace_ref=trace_ref,
                rng=rng,
            )
            tasks.append(task)
            seq += 1

    rng.shuffle(tasks)
    return tasks


def split_and_write(tasks: list, output_dir: str):
    """Split tasks into train/dev/held_out and write as JSONL."""
    out = Path(output_dir)
    n = len(tasks)
    train_end = int(n * 0.50)
    dev_end = train_end + int(n * 0.30)

    partitions = {
        "train": tasks[:train_end],
        "dev": tasks[train_end:dev_end],
        "held_out": tasks[dev_end:],
    }

    counts = {}
    for name, partition in partitions.items():
        path = out / name / "tasks.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            for task in partition:
                f.write(json.dumps(task) + "\n")
        counts[name] = len(partition)
        print(f"  {name}: {len(partition)} tasks → {path}")

    # Write manifest
    manifest = {
        "version": "0.1",
        "total_tasks": n,
        "seed": SEED,
        "partitions": counts,
        "failure_category_counts": {},
        "source_mode_counts": {},
        "difficulty_counts": {},
    }
    for task in tasks:
        cat = task["failure_category"]
        mode = task["source_mode"]
        diff = task["difficulty"]
        manifest["failure_category_counts"][cat] = manifest["failure_category_counts"].get(cat, 0) + 1
        manifest["source_mode_counts"][mode] = manifest["source_mode_counts"].get(mode, 0) + 1
        manifest["difficulty_counts"][diff] = manifest["difficulty_counts"].get(diff, 0) + 1

    with open(out / "manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  manifest: {out / 'manifest.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="tenacious_bench_v0.1/", help="Output directory")
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    print(f"Generating dataset with seed={args.seed}...")
    tasks = generate_all_tasks(seed=args.seed)
    print(f"Generated {len(tasks)} tasks")
    split_and_write(tasks, args.output)
    print("Done.")
