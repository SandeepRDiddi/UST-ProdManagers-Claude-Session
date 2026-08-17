## Context

`costguard.py` today loads `sdlc_token_log.csv` (`task_id, complexity, phase,
model, iteration_loops, input_tokens, output_tokens, total_tokens, cost_usd`)
and prices rows with a flat two-rate `PRICING` table (`input`/`output` per
model tier). `gen_sdlc_log.py` synthesizes that same shape. See proposal.md
for why a finer breakdown and a leak-focused report are needed.

## Goals / Non-Goals

**Goals:**
- Add four new token-type columns and price them per-type.
- Add a `check_cost_leaks` report ranking top-N task-phases by cost with a
  type breakdown, run alongside the existing three checks.
- Keep the existing budget/outlier/hybrid-routing checks' logic and output
  format unchanged (they now just see richer `cost_usd` inputs).

**Non-Goals:**
- No sub-phase (per-call) row granularity — grain stays one row per
  task-phase (see proposal's schema decision below).
- No live/runtime token capture — `gen_sdlc_log.py` remains a synthetic,
  seeded generator, not an instrumentation hook into a real agent.
- No new budget/threshold config for the leak report beyond N (no cap to
  breach — it's a visibility report, not a governance gate).

## Decisions

**Row grain stays task-phase, not per-call.** The propose-phase question
asked whether to also add call-level rows; the token-type breakdown alone
answers "where is the money going by kind of token," which is what "cost
leaks" means here. Per-call rows would double the dataset's dimensionality
(300 rows -> unbounded) for a demo whose value is the *type* breakdown, not
call-count. Kept as a possible future change, not this one.

**New token-type fields, not a single "other_tokens" bucket.** Four named
fields (`cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`,
`tool_use_tokens`) rather than one catch-all, because the leak report's value
is naming *which* type dominates — a lumped bucket would hide that.

**PRICING gets four new rates per model tier, not a shared multiplier.**
Real providers price cache reads/writes and reasoning tokens differently from
each other and from input/output (e.g. cache reads are typically cheaper
than fresh input; reasoning tokens are billed as output-equivalent by some
providers). Illustrative rates, consistent with the existing "illustrative,
not live pricing" disclaimer in README.md:

| type | frontier $/M | efficient $/M |
|---|---|---|
| input | 3.00 | 0.25 |
| output | 15.00 | 1.25 |
| cache_read | 0.30 | 0.03 |
| cache_write | 3.75 | 0.30 |
| reasoning | 15.00 | 1.25 |
| tool_use | 3.00 | 0.25 |

(cache_read ~10% of input; cache_write ~1.25x input, matching common
prompt-caching pricing shapes; reasoning priced as output; tool_use priced as
input — all illustrative, same caveat as existing PRICING.)

**`load_log` fails hard on missing columns** (per spec) rather than
defaulting to 0, because a silent zero-fill would understate cost for any
old-format CSV and make the leak report wrong without any error signal. This
is the reason for `sdlc_token_log.csv` needing full regeneration — no
backward-compat shim.

**`check_cost_leaks` is additive, not a replacement.** It runs after the
existing three checks in `main`, doesn't affect the process exit code (still
governed by budget breaches / outliers only), and defaults N=10 with no CLI
flag added in this change — keeps `main`'s argument surface unchanged.

## Risks / Trade-offs

- [Breaking CSV format change] → Regenerate `sdlc_token_log.csv` via
  `gen_sdlc_log.py` as part of this change; no dual-format support needed
  since this is a demo dataset, not external input.
- [Illustrative per-type pricing may look overly precise] → README.md's
  existing pricing caveat is extended to cover the new rates explicitly.
- [Six-way sum for `total_tokens` is easy to get inconsistent between
  `gen_sdlc_log.py` and `costguard.py`] → Both derive `total_tokens` by
  summing the six fields at the point of construction/load, never by an
  independently-tracked counter.

## Migration Plan

1. Extend `gen_sdlc_log.py` to synthesize the four new fields and updated
   `PRICING`; regenerate `sdlc_token_log.csv`.
2. Extend `costguard.py`'s `load_log`, `PRICING`, cost math, and add
   `check_cost_leaks`; wire it into `main`.
3. Update `test_costguard.py` fixtures (all hand-written CSV rows in tests
   need the new columns) and add leak-report tests.
4. Update `README.md`'s Files/Quickstart/Numbers sections.

No rollback complexity beyond reverting the commit — no external consumers
of `sdlc_token_log.csv`'s schema.
