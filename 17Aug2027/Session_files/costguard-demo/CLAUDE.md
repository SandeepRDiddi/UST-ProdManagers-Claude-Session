# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

CostGuard: governance-as-code demo tool for agentic SDLC token spend. Checks a
simulated token-cost log against a versioned budget config and flags three
failure patterns: per-phase budget breaches (Govern), non-linear complexity
cost outliers (Measure), and hybrid-model-routing waste (Manage).

## Commands

```bash
# Run the tool against the checked-in dataset
python3 costguard.py sdlc_token_log.csv budget_config.yaml

# Run tests
python3 -m pytest test_costguard.py -v

# Run a single test
python3 -m pytest test_costguard.py::test_over_budget_task_is_flagged -v

# Regenerate sdlc_token_log.csv from scratch (seeded, reproducible)
python3 gen_sdlc_log.py
```

`costguard.py` exits 1 if any phase is over budget or any complexity outlier
is flagged, 0 otherwise — used as a CI-style gate.

Note: `gen_sdlc_log.py` writes to a hardcoded path
(`/mnt/user-data/outputs/sdlc_token_log.csv`), not the repo root — copy the
output over `sdlc_token_log.csv` if regenerating the checked-in dataset.

## Architecture

Three files form a pipeline, each independently runnable:

1. **`gen_sdlc_log.py`** — synthesizes `sdlc_token_log.csv`: 50 tasks × 6 SDLC
   phases (Spec, Plan, Implement, Test, Review, Debug) = 300 records. Encodes
   the domain assumptions the whole demo rests on: cubic token scaling with
   complexity up to complexity=3 (`complexity ** 3`), dampened growth beyond
   that, Review/Debug getting extra cost from iteration-loop retries, and only
   35% of eligible low-complexity Spec/Plan tasks actually being routed to the
   cheap model (the rest is the "waste" CostGuard exists to catch).

2. **`budget_config.yaml`** — the enforced policy: per-phase USD caps,
   `complexity_outlier_multiplier` (flag a task costing more than this
   multiple of the average for its complexity tier), and which
   phases/complexity levels are eligible for hybrid routing to a cheaper
   model. This file is the thing governance changes go through — not a
   runtime flag `costguard.py` accepts.

3. **`costguard.py`** — reads the CSV + budget YAML, runs three checks in
   sequence (`check_phase_budgets`, `check_complexity_outliers`,
   `check_hybrid_routing_waste`), prints a report, and exits non-zero on any
   flag. `PRICING` (frontier vs. efficient model $/M tokens) is duplicated
   here and in `gen_sdlc_log.py` — keep them in sync if pricing changes,
   since `check_hybrid_routing_waste` uses it to compute hypothetical savings
   against the actual logged tokens.

Tests (`test_costguard.py`) exercise the check functions directly against
both synthetic fixtures (`tmp_path`-written CSVs) and the real checked-in
`sdlc_token_log.csv` + `budget_config.yaml`, asserting the real dataset flags
exactly the Review phase and finds positive hybrid-routing savings — i.e.
they pin the specific numbers this demo depends on, not just generic
pass/fail behavior.

## Numbers this demo is calibrated to

All figures reproduced by actually running the pipeline, not invented —
see README.md for the specific results (total spend, phase % breakdown,
complexity scaling ratio, budget breaches, recoverable hybrid-routing waste)
and the illustrative token pricing assumptions.

## OpenSpec

This repo uses OpenSpec (`openspec/` dir, `.claude/` skills/commands) for
spec-driven change proposals. Start a change with `/opsx:propose "idea"`.
