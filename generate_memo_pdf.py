"""Generate memo.pdf — exactly two pages."""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

W, H = LETTER
MARGIN = 0.75 * inch

doc = SimpleDocTemplate(
    "memo.pdf",
    pagesize=LETTER,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=0.6 * inch, bottomMargin=0.6 * inch,
)

styles = getSampleStyleSheet()

title   = ParagraphStyle("title",   fontSize=13, fontName="Helvetica-Bold",
                          spaceAfter=2, leading=16)
sub     = ParagraphStyle("sub",     fontSize=9,  fontName="Helvetica",
                          spaceAfter=6, textColor=colors.HexColor("#444444"))
h1      = ParagraphStyle("h1",      fontSize=11, fontName="Helvetica-Bold",
                          spaceBefore=8, spaceAfter=3, leading=14)
h2      = ParagraphStyle("h2",      fontSize=9.5, fontName="Helvetica-Bold",
                          spaceBefore=5, spaceAfter=2, leading=12)
body    = ParagraphStyle("body",    fontSize=8.5, fontName="Helvetica",
                          leading=12, spaceAfter=4)
small   = ParagraphStyle("small",   fontSize=7.5, fontName="Helvetica",
                          leading=11, spaceAfter=3,
                          textColor=colors.HexColor("#333333"))
italic  = ParagraphStyle("italic",  fontSize=8.5, fontName="Helvetica-Oblique",
                          leading=12, spaceAfter=4)

def hr():
    return HRFlowable(width="100%", thickness=0.5,
                      color=colors.HexColor("#AAAAAA"), spaceAfter=4, spaceBefore=4)

def sp(h=4):
    return Spacer(1, h)

TABLE_STYLE = TableStyle([
    ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
    ("FONTSIZE",    (0, 0), (-1, -1), 8),
    ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#EEEEEE")),
    ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#BBBBBB")),
    ("TOPPADDING",  (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING",(0,0), (-1, -1), 3),
    ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ("RIGHTPADDING",(0, 0), (-1, -1), 5),
    ("ALIGN",       (1, 1), (-1, -1), "RIGHT"),
])

story = []

# ── PAGE 1 ───────────────────────────────────────────────────────────────────

story.append(Paragraph("Tenacious-Bench v0.1 — Final Evaluation Memo", title))
story.append(Paragraph(
    "Eyobed Feleke &nbsp;·&nbsp; eyobed@10academy.org &nbsp;·&nbsp; 2026-05-02", sub))
story.append(hr())

story.append(Paragraph("Page 1 — The Decision", h1))

story.append(Paragraph("Executive Summary", h2))
story.append(Paragraph(
    "A CPO-trained Qwen2.5 0.5B judge, fine-tuned on 137 Tenacious-Bench preference "
    "pairs, correctly classifies <b>92.7%</b> of held-out compliance tasks (51/55) "
    "versus <b>69.1%</b> for the rule-only baseline — a <b>+23.6 pp gain "
    "(95% CI: [+9.8, +37.4], McNemar p=0.004)</b> — while adding zero marginal cost "
    "at inference. The trained judge closes three of four documented failure modes "
    "(honesty flag bypass, bench overcommitment, tone drift) but still requires the "
    "rule-based layer for scheduling and format checks; the recommended deployment is "
    "a hybrid: rule-only as a hard gate, CPO judge as the semantic layer, with a "
    "human-review trigger for low-confidence outputs.", body))

story.append(Paragraph("Headline Lift — Delta A", h2))

t1 = Table(
    [
        ["Condition", "Held-out Accuracy", "Pass Rate", "Cost / task"],
        ["Rule-only baseline",          "69.1% (38/55)", "61.8%", "$0.000"],
        ["Prompt-eng (3-shot Haiku)",   "78.2% (43/55)", "65.5%", "$0.001"],
        ["CPO judge v1 (trained)",      "92.7% (51/55)", "67.3%", "$0.000"],
        ["Claude Sonnet API (est.)",    "~96.0%",         "~68%",  "$0.003"],
    ],
    colWidths=[2.5*inch, 1.5*inch, 1.0*inch, 1.0*inch],
)
t1.setStyle(TABLE_STYLE)
story.append(t1)
story.append(sp(4))
story.append(Paragraph(
    "<b>Delta A = +23.6 pp</b> over rule-only (95% CI: [+9.8 pp, +37.4 pp], "
    "McNemar χ²=8.47, p=0.004). Largest per-category gains: multithread-leakage "
    "+70 pp, cost-pathology +50 pp, dual-control +38 pp.", small))

story.append(Paragraph("Delta B — Honest Report", h2))
story.append(Paragraph(
    "<b>Delta B = +14.5 pp</b> over 3-shot prompt-engineering "
    "(95% CI: [+1.6 pp, +27.4 pp], McNemar p=0.043). The lower bound (+1.6 pp) is "
    "near zero — a stronger few-shot baseline would narrow this gap. The advantage of "
    "the trained judge is not accuracy alone: it costs <b>$0.000/task</b> versus "
    "$0.001/task for prompt-engineering and was trained on the exact violation types "
    "in the Tenacious domain.", body))

story.append(Paragraph("Cost Per Task", h2))
t2 = Table(
    [
        ["Mode", "Cost/task", "Cost/1k tasks", "Notes"],
        ["Rule-only",              "$0.000", "$0.00",  "No API call"],
        ["CPO judge (local 4-bit)","$0.000", "$0.00",  "Runs on CPU after quantization"],
        ["Prompt-eng (Haiku)",     "$0.001", "$0.80",  "3-shot, ~800 tokens/call"],
        ["Claude Sonnet judge",    "$0.003", "$3.30",  "Full eval-tier, not deployed"],
    ],
    colWidths=[2.1*inch, 0.85*inch, 1.0*inch, 2.05*inch],
)
t2.setStyle(TABLE_STYLE)
story.append(t2)
story.append(sp(4))

story.append(Paragraph("Deployment Recommendation", h2))
story.append(Paragraph(
    "<b>Deploy with caveat.</b> Deploy the hybrid system: (1) rule-only hard gate "
    "for format/length/banned-phrase violations, (2) CPO judge for semantic compliance "
    "(honesty flags, signal grounding), (3) human-review queue for judge scores in "
    "[0.60–0.75]. Caveat: the judge was trained on 137 pairs — half the minimum "
    "recommended by Liu et al. (2024) for this task complexity. ICP misclassification "
    "accuracy (96%) masks insufficient coverage of diverse disqualification scenarios. "
    "Deploy on four high-confidence categories first (signal-overclaiming, tone-drift, "
    "bench-overcommitment, dual-control); gate ICP misclassification behind human "
    "review until training data doubles.", body))

story.append(Paragraph("— page break —",
    ParagraphStyle("pb", fontSize=7, textColor=colors.white,
                   pageBreakAfter="always", spaceAfter=0)))

# ── PAGE 2 ───────────────────────────────────────────────────────────────────

story.append(Paragraph("Page 2 — The Skeptic's Appendix", h1))

story.append(Paragraph("Four Failure Modes v0.1 Does Not Capture", h2))

failures = [
    ("<b>1. Multi-turn context degradation.</b>",
     "All 274 tasks are single-turn (brief → email). Agents operating in a thread "
     "context accumulate prior turns that can override active honesty flags. "
     "<i>v0.2 addition:</i> multi-turn trace tasks with session-state honesty flags."),
    ("<b>2. Cross-prospect data leakage.</b>",
     "When an agent processes briefs for multiple prospects in a batch, signals from "
     "prospect A can leak into prospect B's email. No v0.1 task tests for "
     "cross-contamination. <i>v0.2 addition:</i> paired tasks where the second task "
     "contains a signal that should only be present in the first."),
    ("<b>3. Partial flag acknowledgment.</b>",
     "The rubric marks FAIL if any banned pattern from an active flag appears. "
     "A finer failure mode is partial acknowledgment: agent hedges one flag correctly "
     "while ignoring a second. The binary FAIL verdict does not distinguish "
     "\"ignored all flags\" from \"ignored one of three flags.\" "
     "<i>v0.2 addition:</i> per-flag scoring with a minimum-satisfied-flags threshold."),
    ("<b>4. Prospect response simulation.</b>",
     "The benchmark evaluates the outbound email in isolation and does not assess "
     "whether a compliant email elicits a positive response. A score-1.0 email can "
     "still be a weak opener. <i>v0.2 addition:</i> a prospect-response simulator "
     "that rates conversion likelihood independently of compliance."),
]

for label, text in failures:
    story.append(Paragraph(label + " " + text, small))

story.append(Paragraph("Public-Signal Lossiness in Ground Truth", h2))
story.append(Paragraph(
    "Hiring signals, AI maturity scores, and leadership signals are synthetic "
    "parameters drawn from public data <i>schemas</i> (Crunchbase field structures, "
    "LinkedIn job post patterns) but not from live scrapes. The benchmark does not "
    "test signal staleness (a hiring signal true six months ago but no longer active), "
    "and the AI maturity score is a numeric placeholder, not a real inferred score "
    "from a production signal pipeline. Ground truth labels are reliable for the "
    "rubric dimensions as written; the rubric itself does not capture signal "
    "temporality. Any agent that correctly handles synthetic signals still needs "
    "separate evaluation on live-signal inputs before production deployment.", small))

story.append(Paragraph("One Honest Unresolved Training Failure", h2))
story.append(Paragraph(
    "The CPO judge has a <b>PASS bias on ICP misclassification tasks</b>. Tasks where "
    "the prospect is disqualified but the email looks compliant (no banned phrases, "
    "correct format, generic but not lying) score 1.0 on three of four rubric "
    "dimensions before the judge is applied. The judge learns surface compliance "
    "correctly but cannot reliably detect the policy-level suppression decision "
    "(this prospect should receive no email at all) from the email text alone. "
    "ICP misclassification accuracy is 96% in ablations — but this largely reflects "
    "structural email properties, not the suppression decision. "
    "This failure mode is unresolved and requires a separate ICP classifier gate "
    "upstream of the email judge.", small))

story.append(Paragraph("Kill-Switch Trigger Condition", h2))
story.append(Paragraph(
    "Trigger the kill-switch and revert to rule-only if any of the following are "
    "observed in production:", small))

triggers = [
    "The judge's false-negative rate on <b>layoff_overrides_funding violations exceeds "
    "5%</b> over a 7-day rolling window (measured via weekly audit of 50 randomly "
    "sampled judge-approved emails). A false negative sends a growth pitch to a "
    "company in active workforce reduction — direct reputational risk.",
    "The judge approves any email containing a <b>specific banned phrase from "
    "Style Guide v2</b> that also appears in a tone-drift violation documented in "
    "the training data. This indicates regression on a learned pattern.",
    "<b>Classification accuracy on the dev partition drops below 70%</b> after any "
    "model update or quantization change — measured by running "
    "<i>scoring_evaluator.py --batch tenacious_bench_v0.1/dev/ --no-llm</i> on "
    "merged weights before deployment.",
]

for i, t in enumerate(triggers, 1):
    story.append(Paragraph(f"{i}. {t}", small))

story.append(sp(6))
story.append(hr())
story.append(Paragraph(
    "<i>All numeric claims mapped to source files in evidence_graph.json. "
    "Full methodology: methodology_rationale.md. Training artifacts: training/. "
    "Ablations: ablations/.</i>",
    ParagraphStyle("foot", fontSize=7, fontName="Helvetica-Oblique",
                   textColor=colors.HexColor("#666666"), leading=10)))

doc.build(story)
print("memo.pdf written")
