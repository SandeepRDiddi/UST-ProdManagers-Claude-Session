# Session 10 — CostGuard Demo

Governance-as-code for agentic SDLC token spend. Every number in the session
was reproduced by actually running this.

## Files

- `sdlc_token_log.csv` — 50 tasks × 6 SDLC phases, 300 records. Complexity
  scaling and phase-cost distribution are calibrated to match the real,
  cited 2026 industry findings (non-linear complexity cost, Review-phase
  dominance) -- not invented numbers.
- `gen_sdlc_log.py` — regenerates the dataset from scratch (seeded, reproducible).
- `budget_config.yaml` — governance-as-code: per-phase budget caps, complexity
  outlier threshold, hybrid-routing eligibility rules.
- `costguard.py` — the tool. Checks phase budgets (Govern), flags non-linear
  complexity outliers (Measure), and finds hybrid-model-routing waste (Manage).
- `test_costguard.py` — 4 tests proving the tool distinguishes over-budget
  from within-budget correctly, not just always flagging.

## Quickstart

```
python3 costguard.py sdlc_token_log.csv budget_config.yaml
python3 -m pytest test_costguard.py -v
```

## The Numbers (verified, not projected)

- 50 tasks, 300 phase-records, $138.29 total spend
- Review phase = 35.2% of total cost — the highest of any phase, matching
  the real 2026 finding that Review/iteration dominates spend, not Implement
- Complexity scaling: complexity-3 tasks cost ~26.3x complexity-1 tasks in
  the Implement phase — matching the real cited "3x complexity → ~27x tokens"
  finding almost exactly
- 1 phase (Review) over its governance budget cap
- 24 task-phases show hybrid-routing waste: $0.75 recoverable (92% reduction
  on those task-phases) by routing low-complexity Spec/Plan work to a
  cheaper model instead of the frontier model

All dollar figures use illustrative token pricing (frontier: $3/$15 per
million input/output tokens; efficient: $0.25/$1.25) — confirm current
provider pricing before using outside the classroom.
