# Tenacious Style Guide v2
# B2B Outbound Email — Tone Preservation Specification

**Version:** 2.0  
**Status:** Canonical reference — all dataset tasks scored against this spec  
**Applies to:** All candidate email outputs evaluated by Tenacious-Bench v0.1

---

## 1. The Five Tone Markers

Every compliant email must embody all five markers simultaneously.

### 1.1 Direct
State the point within the first two lines. No preamble ("I hope this email finds you well"), no warm-up paragraph, no context-setting that doesn't earn its place.

**Good:** "Saw 4 open data engineering roles at DataFlow since Q1. Tenacious has dbt engineers available."  
**Bad:** "I hope this email finds you well. I wanted to reach out because I came across your company and thought there might be an interesting opportunity to connect."

### 1.2 Grounded
Every claim must trace back to a signal from the prospect brief. Observations about the prospect's team, roadmap, or competitive position are only permitted if the brief contains the underlying evidence.

**Good:** "3 open ML roles and a public blog post on LLM fine-tuning — looks like you're building in this space."  
**Bad:** "As an AI-first company, your roadmap demands top-tier ML talent." (no AI maturity signal in brief)

### 1.3 Honest
Do not assert what you do not know. Honesty flags in the prospect brief are non-negotiable constraints. If `weak_hiring_velocity_signal` is active, you may not characterize the hiring as "aggressive" or "fast-scaling." If `layoff_overrides_funding` is active, do not pitch growth support or congratulate on funding.

**Good:** "Noticed 2 open engineering roles — not a clear growth signal, but curious if there's a specific gap worth discussing."  
**Bad:** "Your team is scaling fast — Tenacious can help you grow at this pace."

### 1.4 Professional
No pressure tactics. No scarcity framing. No urgency manufacture. No begging language. No apologies for sending a cold email. Write as you would to a respected colleague you haven't met.

**Good:** "Worth a 20-minute call if this is relevant?"  
**Bad:** "Don't miss out — our top engineers are moving fast!", "You'll regret not taking this call."

### 1.5 Non-Condescending
Frame observations as research findings, not deficit verdicts. Never tell the prospect their team is "behind," "underdeveloped," "clearly lacking," or needs to "catch up." The LinkedIn-Roast Test applies: if this sentence would be quoted mockingly in a screenshot, it fails.

**Good:** "Two peer companies show dedicated ML headcount. Curious if that's a gap you've scoped."  
**Bad:** "Your AI function is clearly underdeveloped compared to sector leaders.", "Your competitors are significantly ahead of you."

---

## 2. Complete Banned Phrase List

The following patterns are ALWAYS prohibited regardless of context.

### 2.1 Buzzwords and Jargon
- world-class
- leverage (as a verb applied to people or teams)
- ecosystem (when referring to talent)
- top talent
- A-players
- rockstar / rock star
- ninja
- synergy / synergistic
- supercharge
- cutting-edge
- game-changer / game changer
- disruptor / disruptive
- paradigm shift
- skyrocket
- wizard
- our proprietary (any variant)
- innovative solution(s)
- best-in-class

### 2.2 Re-engagement Clichés
- circling back
- following up again
- just checking in
- just wanted to touch base
- looping back
- Per my last email
- As per my previous email

### 2.3 Pressure and Urgency Tactics
- Don't miss out
- You'll regret
- Limited availability
- Act now
- Last chance
- Urgent

### 2.4 Opener Clichés
- I hope this email finds you well
- Hope you're doing well
- I wanted to reach out
- I came across your profile/company
- our [X] employees (headcount flex)

### 2.5 External "Bench" References
- bench (when used as a noun referring to Tenacious's talent inventory)
- our bench
- bench of engineers
- from our bench
- available on the bench

*Rationale: "bench" is internal operations language. Externally it sounds transactional and reduces engineers to fungible inventory. Use "available engineers," "engineers we work with," or "engineers on our current roster" instead.*

### 2.6 Format Violations
- Exclamation marks (!) anywhere in subject or body
- Subject line exceeding 60 characters
- Body exceeding 120 words
- Subject that does not start with one of: Request:, Follow-up:, Context:, Question:

---

## 3. Subject Line Prefix Rule

All subject lines must begin with one of four canonical prefixes:

| Prefix | Use when |
|---|---|
| `Request:` | Explicitly asking for something (a call, a response, a referral) |
| `Follow-up:` | Continuing a prior thread or conversation |
| `Context:` | Providing unsolicited context the prospect may find relevant |
| `Question:` | Asking a genuine question about their situation |

The prefix must be followed by a colon and a space, then the subject content. The total subject length must not exceed 60 characters including the prefix.

**Good:** "Question: ML capacity at DataFlow Technologies" (46 chars ✓)  
**Bad:** "Congrats on your Series B — scaling next?" (no prefix ✗)  
**Bad:** "Question: wondering if you would be interested in discussing your team's engineering capacity goals for the coming quarter" (too long ✗)

---

## 4. The LinkedIn-Roast Test

Before finalizing any draft, apply this test: *Would this sentence be screenshot-shared with a snarky caption on LinkedIn?*

Automatic failures:
- Any sentence that tells the prospect their team is behind, failing, or underdeveloped
- Any sentence that asserts what the prospect "needs" without their input
- Any re-engagement message that leads with guilt or pressure
- Exclamation marks paired with superlatives ("world-class engineers!")

If a sentence passes the roast test, it may still fail the rubric for other reasons. Passing the roast test is necessary but not sufficient.

---

## 5. Six-Step Outreach Decision Flow

Before generating or approving any email, step through this flow:

1. **ICP check** — Does the prospect meet all ICP inclusion criteria? If not, suppress outreach entirely.
2. **Honesty flag review** — List all active flags. Map each flag to its prohibited claim type.
3. **Signal inventory** — What specific signals are available? Name at least one to ground the email.
4. **Tone check** — Does the draft contain any banned phrases? Does the subject start with the right prefix?
5. **Format check** — Subject ≤ 60 chars, body ≤ 120 words, no exclamation marks.
6. **LinkedIn-Roast Test** — Would this be mocked? If yes, revise before sending.

Any "no" at step 1 → suppress. Any "yes" at step 6 → revise. Steps 2–5 are hard gates.

---

## 6. Labeled Drafts (24 Examples)

### 6.1 Good Drafts (12)

**GOOD-01** — Category: tone-drift | All 5 tone markers ✓
```
Subject: Question: engineering capacity at Cascade Fintech
Body: Hi [Name],

Saw 4 open backend engineering roles at Cascade since Q1. Tenacious has Go engineers available.

Worth a 20-minute call to see if the count and timeline match your need?

[Calendar link]
```

**GOOD-02** — Category: signal-overclaiming | Acknowledges signal uncertainty ✓
```
Subject: Context: ML roles at Vertex Analytics
Body: Hi [Name],

Noticed 2 open ML roles at Vertex — small sample, so hard to read the velocity, but there's signal. Tenacious has ML engineers available if there's a capacity gap worth scoping.

Worth a 20-minute call?

[Calendar link]
```

**GOOD-03** — Category: bench-overcommitment | Checks capacity before claiming ✓
```
Subject: Question: Go microservices capacity at Apex DevOps
Body: Hi [Name],

Saw open Go microservices roles at Apex. We have Go engineers available — worth a 30-minute call to see whether the headcount and timeline match your need before I confirm capacity?

[Calendar link]
```

**GOOD-04** — Category: gap-overclaiming | Frames gap as research finding ✓
```
Subject: Context: ML headcount in your sector
Body: Hi [Name],

Two peer companies in your segment show dedicated ML headcount. Curious whether that reflects a gap you've scoped or a deliberate choice to build differently.

Worth a call?

[Calendar link]
```

**GOOD-05** — Category: signal-overclaiming | Respects layoff override flag ✓
```
Subject: Question: engineering priorities at Echo Health
Body: Hi [Name],

Saw the recent team changes at Echo. If you're rebuilding capacity in data engineering, Tenacious has engineers available.

Worth a 20-minute call when the timing is right?

[Calendar link]
```

**GOOD-06** — Category: tone-drift | Follow-up without pressure ✓
```
Subject: Follow-up: engineering capacity at Helix Data
Body: Hi [Name],

Following up on my note from last week. No pressure — just want to make sure this landed. If the timing isn't right, happy to revisit.

[Calendar link]
```

**GOOD-07** — Category: icp-misclassification | Correctly flags ICP disqualification ✓
```
[SUPPRESS — ICP DISQUALIFIED]
Reason: Prospect exhibits disqualifying condition (solo founder, no eng team). Outreach suppressed per Step 1 of decision flow.
```

**GOOD-08** — Category: signal-reliability | Caveats low-confidence signal ✓
```
Subject: Question: data infrastructure direction at Summit AI
Body: Hi [Name],

Saw a job post suggesting a dbt migration — hard to confirm from outside, but if the data stack is in transition, Tenacious has engineers who've run that migration a few times.

Worth a call?

[Calendar link]
```

**GOOD-09** — Category: dual-control | Applies both hiring and AI flags ✓
```
Subject: Context: engineering signal at Prism Analytics
Body: Hi [Name],

Saw 2 open engineering roles and some early AI tooling signal at Prism. Both signals are weak, so I won't make claims about your direction — just want to check whether there's a capacity gap worth discussing.

[Calendar link]
```

**GOOD-10** — Category: tone-drift | Short, direct, no condescension ✓
```
Subject: Request: 20 minutes on data engineering at Relay Infrastructure
Body: Hi [Name],

3 open data engineering roles at Relay since February. Tenacious has engineers available.

Worth a 20-minute call?

[Calendar link]
```

**GOOD-11** — Category: signal-overclaiming | Tech stack flag respected ✓
```
Subject: Question: backend capacity at Ironclad Security
Body: Hi [Name],

Noticed backend engineering roles at Ironclad. We work with engineers across several backend stacks — worth a call to see if there's a match before I make assumptions about your environment?

[Calendar link]
```

**GOOD-12** — Category: tone-drift | Multi-signal, under 120 words ✓
```
Subject: Context: engineering signal at NovaMed AI
Body: Hi [Name],

3 open ML roles and a public model evaluation post from your team — looks like you're building production ML capability. Tenacious has ML engineers available.

Worth a 20-minute call to see if the headcount and timeline make sense?

[Calendar link]
```

---

### 6.2 Bad Drafts (12)

**BAD-01** — Category: tone-drift | Exclamation marks + buzzwords ✗
```
Subject: Helping Cascade Fintech leverage world-class ML talent!
Body: Hi [Name],

We'd love to help Cascade Fintech leverage our ecosystem of world-class A-players and top talent to supercharge your ML roadmap! Our rockstar engineers have synergy with your stack. We can definitely help!

[Calendar link]
```
*Violations: exclamation marks (3), world-class, leverage, ecosystem, A-players, top talent, rockstar, synergy, supercharge, subject prefix missing*

**BAD-02** — Category: tone-drift | Opener cliché ✗
```
Subject: Engineering capacity at Vertex Analytics
Body: Hi [Name],

I hope this email finds you well. I wanted to reach out because I came across Vertex Analytics and thought there might be an interesting opportunity to connect regarding your engineering needs.

[Calendar link]
```
*Violations: "I hope this email finds you well", "I wanted to reach out", "came across", subject prefix missing*

**BAD-03** — Category: tone-drift | Jargon cluster ✗
```
Subject: Your skyrocketing AI roadmap needs game-changer engineers
Body: Hi [Name],

Your company is at a paradigm shift moment in AI development. As a game-changer in your space, you need disruptive engineering talent. Our proprietary matching system connects you with wizard-level engineers who will skyrocket your roadmap.

[Calendar link]
```
*Violations: skyrocket (×2), game-changer, paradigm shift, disruptor, our proprietary, wizard, subject prefix missing, subject > 60 chars*

**BAD-04** — Category: tone-drift | External bench reference ✗
```
Subject: Our bench of engineers ready for your team
Body: Hi [Name],

Tenacious has a deep bench of Go engineers ready to deploy. Our bench has engineers who can match your stack immediately. Engineers from our bench have deployed in similar environments.

[Calendar link]
```
*Violations: bench (×3), subject prefix missing, "ready to deploy"*

**BAD-05** — Category: gap-overclaiming | Condescending framing ✗
```
Subject: Context: your team is behind on AI
Body: Hi [Name],

Your competitors are significantly ahead of you in AI maturity. Your AI function is clearly underdeveloped. Companies in your sector are doing AI-native product development — your team hasn't reached that capability yet.

[Calendar link]
```
*Violations: condescending framing (×3), non-compliant subject (no Question/Request/Context/Follow-up prefix)*

**BAD-06** — Category: signal-overclaiming | Weak signal treated as confirmed ✗
```
Subject: Congrats on scaling — engineering support for Apex DevOps
Body: Hi [Name],

Noticed Apex DevOps is aggressively hiring across engineering — your team is scaling fast. With your rapid growth trajectory, Tenacious can help you grow the team at pace.

[Calendar link]
```
*Violations: "aggressively hiring", "scaling fast", "rapid growth", subject prefix missing*

**BAD-07** — Category: signal-overclaiming | AI maturity asserted without signal ✗
```
Subject: Request: AI-first engineering for NovaMed
Body: Hi [Name],

As an AI-first company, your roadmap demands top-tier ML talent. We understand your AI strategy and can execute on it from day one. Your AI-native approach requires engineers who think in models.

[Calendar link]
```
*Violations: "AI-first", "AI-native", "top-tier" (close to top talent), "your AI strategy" (no AI maturity signal), "AI-native"*

**BAD-08** — Category: bench-overcommitment | Capacity asserted without discovery ✗
```
Subject: Context: Go microservices team ready to deploy
Body: Hi [Name],

We have a Go microservices team ready to deploy for your needs. Our senior engineers can start within two weeks and scale to match your headcount requirement. Capacity confirmed for immediate start.

[Calendar link]
```
*Violations: "team ready to deploy", "senior engineers" (capacity assertion), "Capacity confirmed" (overclaims without discovery call)*

**BAD-09** — Category: tone-drift | Re-engagement clichés ✗
```
Subject: Following up again — wanted to circle back!
Body: Hi [Name],

Just circling back on my previous email! Per my last email, I wanted to loop back and make sure you saw my note. Just checking in — as per my previous message, would love to connect!

[Calendar link]
```
*Violations: exclamation marks (×3), "circling back", "Per my last email", "loop back", "Just checking in", "as per my previous", subject prefix missing*

**BAD-10** — Category: tone-drift | Pressure tactics ✗
```
Subject: Don't miss out on top engineering talent
Body: Hi [Name],

Our top engineers are moving fast — don't miss out. You'll regret not taking this call. This is a limited availability situation and we can't hold this capacity indefinitely.

Act now to secure your slot.

[Calendar link]
```
*Violations: "Don't miss out", "You'll regret", "Limited availability", "Act now", "top engineers", subject prefix missing*

**BAD-11** — Category: tone-drift | Length violation ✗
```
Subject: Context: engineering capacity and ML talent availability at DataFlow Technologies for your Q2 roadmap expansion
Body: Hi [Name],

I wanted to reach out because I noticed DataFlow Technologies has been posting a significant number of engineering and ML roles over the past several months, and I thought this might be relevant to your current team expansion plans. We work with a wide range of engineers across multiple tech stacks and disciplines, and I believe we could provide meaningful support for your roadmap. Our engineers have experience across a variety of domains including data engineering, machine learning, backend development, and infrastructure — making them a versatile fit for companies at different stages of growth.

I'd love to schedule a call at your convenience to discuss how we might be able to support your hiring needs going forward.

[Calendar link]
```
*Violations: subject > 60 chars, subject prefix missing (starts with "Context:" but then runs too long), body > 120 words, "I wanted to reach out"*

**BAD-12** — Category: icp-misclassification | Sent despite disqualifying condition ✗
```
Subject: Request: engineering capacity support at early-stage startup
Body: Hi [Name],

Tenacious can help scale your engineering capacity. With your growth trajectory, our engineers can accelerate delivery across your roadmap.

Worth a 20-minute call?

[Calendar link]
```
*Violations: outreach sent despite prospect being a pre-ICP early-stage company with no clear product/revenue signal, generic pitch with no specific signal reference*
