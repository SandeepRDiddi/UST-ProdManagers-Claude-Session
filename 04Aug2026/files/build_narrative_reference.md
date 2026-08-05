# Build Narrative — drift_watcher agent
(Reference example for Lab 3 — Articulate Value in the Build Narrative)
Structured using SCQA (Situation–Complication–Question–Answer),
Barbara Minto's Pyramid Principle — the standard framework for structuring
an executive-ready narrative from a technical finding.

## Situation
notification-service's README describes three operating characteristics —
supported channels, retry policy, and rate limit — that every downstream
team relies on when planning capacity, setting client expectations, or
scoping new integrations.

## Complication
All three documented characteristics are wrong, and have been for between
7 weeks and 4 months. Each drifted for a legitimate engineering reason
(a new channel shipped, a retry storm was fixed, a quota incident forced a
lower limit) — but none of those changes reached the document. Anyone who
trusted the README during that window was planning against a system that
doesn't exist.

## Question
How do we make sure this stops being something we discover by accident,
three months later, in a client conversation — for this service, and for
every other service like it?

## Answer
Deploy `drift_watcher.py`: a context-aware agent configured on an explicit
hypothesis (`context_claims.yaml`) that checks documentation claims against
Rank 1–3 sources on the Trust Hierarchy — source code and machine-enforced
config, never the docs themselves — on every merge. It already caught all
three real discrepancies in this repo, with zero false positives, verified
by its own test suite. The same pattern (one YAML file naming the claims
that matter, one script checking them) generalizes to any service: the fix
for "docs lie" isn't better discipline, it's a mechanism that makes lying
impossible to do silently.

## The One-Line Version (for a slide, or a Slack message to a VP)
*"We found three ways our documentation has been wrong for months, wrote a
15-minute check that would have caught all three the day they happened, and
it's ready to run in CI today."*
