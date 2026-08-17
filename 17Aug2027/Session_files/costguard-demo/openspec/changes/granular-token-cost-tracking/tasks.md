## 1. Dataset generator (gen_sdlc_log.py)

- [ ] 1.1 Extend `PRICING` with `cache_read`, `cache_write`, `reasoning`,
      `tool_use` rates for both `frontier` and `efficient` tiers (per
      design.md's rate table).
- [ ] 1.2 Add synthesis logic for `cache_read_tokens`, `cache_write_tokens`,
      `reasoning_tokens`, `tool_use_tokens` per row (seeded via the existing
      `rng`, reproducible).
- [ ] 1.3 Recompute `total_tokens` as the sum of all six token-type fields.
- [ ] 1.4 Recompute `cost_usd` by pricing all six token types at their
      model-tier rate.
- [ ] 1.5 Regenerate `sdlc_token_log.csv` with the new columns.

## 2. Core tool (costguard.py)

- [ ] 2.1 Extend `PRICING` to match `gen_sdlc_log.py`'s new rates.
- [ ] 2.2 Update `load_log` to parse and require
      `cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`,
      `tool_use_tokens`; raise a clear error naming any missing column(s).
- [ ] 2.3 Add a per-record cost-by-type helper (used by both
      `check_hybrid_routing_waste`'s hypothetical-cost math and the new leak
      report) so pricing logic isn't duplicated.
- [ ] 2.4 Implement `check_cost_leaks(rows, top_n=10)`: rank task-phase
      records by `cost_usd` descending, print `task_id`, `phase`, total
      cost, and the per-token-type cost contribution for each of the top N.
- [ ] 2.5 Wire `check_cost_leaks` into `main`, after the existing three
      checks; keep exit-code logic based only on budget breaches and
      outliers (unchanged).

## 3. Tests (test_costguard.py)

- [ ] 3.1 Update existing hand-written CSV fixtures in
      `test_within_budget_raises_no_flag` and
      `test_over_budget_task_is_flagged` to include the four new columns.
- [ ] 3.2 Add a test asserting `cost_usd` reflects cache/reasoning/tool-use
      token contributions, not just input/output.
- [ ] 3.3 Add a test asserting `load_log` raises on a CSV missing the new
      token-type columns.
- [ ] 3.4 Add a test asserting `check_cost_leaks` ranks by cost descending
      and returns entries independent of budget/outlier status (e.g. a
      high-cost, within-budget record still appears in the top N).
- [ ] 3.5 Add a test asserting `check_cost_leaks` handles fewer records than
      `top_n` without error.
- [ ] 3.6 Run full suite against the regenerated real dataset
      (`sdlc_token_log.csv` + `budget_config.yaml`) and confirm
      `test_real_dataset_flags_exactly_review` and
      `test_real_dataset_finds_hybrid_waste` still pass with the new pricing.

## 4. Docs

- [ ] 4.1 Update `README.md` Files section to describe the new columns and
      the `check_cost_leaks` report.
- [ ] 4.2 Update `README.md` Numbers section with any changed totals from
      the regenerated dataset (new pricing changes total spend).
- [ ] 4.3 Extend `README.md`'s pricing caveat to cover the four new
      illustrative rates.
