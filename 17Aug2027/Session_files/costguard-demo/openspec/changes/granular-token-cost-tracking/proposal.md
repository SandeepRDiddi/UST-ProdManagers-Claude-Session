## Why

CostGuard currently records cost at task-phase granularity only (input/output
tokens, one model per row). It cannot show *why* a phase is expensive — it
can't distinguish cache-miss waste, reasoning overhead, or tool-use spend from
plain generation, and it has no report that simply ranks where the money is
going independent of budget caps or outlier math. The user wants finer token
attribution and a direct "where are my cost leaks" view.

## What Changes

- Extend the token-cost schema with a type-level breakdown per task-phase
  record: cache-read tokens, cache-write tokens, reasoning tokens, and
  tool-use tokens, each priced independently alongside existing input/output.
- Extend `gen_sdlc_log.py` to synthesize these new token-type fields
  (seeded, reproducible) so the checked-in dataset reflects them.
- Extend `costguard.py`'s cost calculation to price every token type, not
  just input/output.
- Add a new CLIENT-facing report, `check_cost_leaks`, that ranks task-phases
  by total cost descending (Top-N) and prints each one's token-type
  breakdown, so the highest-cost contributors are visible independent of
  whether they breach a budget cap or outlier threshold.
- **BREAKING**: `sdlc_token_log.csv` schema gains new required columns
  (`cache_read_tokens`, `cache_write_tokens`, `reasoning_tokens`,
  `tool_use_tokens`); `load_log` requires the new columns, so old CSVs
  without them will fail to load.

## Capabilities

### New Capabilities
- `token-cost-attribution`: token-type-level breakdown (cache-read,
  cache-write, reasoning, tool-use, input, output) captured per task-phase
  record and priced independently.
- `cost-leak-report`: a Top-N cost-contributor report that ranks task-phases
  by cost and shows their token-type breakdown, independent of budget/outlier
  checks.

### Modified Capabilities
(none — existing budget/outlier/hybrid-routing checks are unchanged; they
gain access to richer per-type cost but keep current pass/fail behavior)

## Impact

- `gen_sdlc_log.py`: new token-type fields in synthesized rows; `PRICING`
  table extended with cache/reasoning/tool-use rates.
- `costguard.py`: `load_log` parses new columns; `PRICING` extended to match;
  new `check_cost_leaks` function; `main` calls it and includes it in the
  summary line.
- `sdlc_token_log.csv`: regenerated with new columns (breaking format change).
- `test_costguard.py`: new tests for `check_cost_leaks` and for cost
  calculation including the new token types.
- `README.md`: update Files/Quickstart/Numbers sections to describe the new
  columns and report.
