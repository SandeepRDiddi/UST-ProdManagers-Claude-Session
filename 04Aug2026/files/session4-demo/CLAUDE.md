# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Demo of a **context-aware drift-detection agent**. `README.md` documents notification-service behavior that has since drifted from reality (3 changes landed, docs never updated — see `CHANGELOG.md`). `drift_watcher.py` is the agent: it checks `context_claims.yaml` (the README's claims, mapped to their real source) against Rank 1-3 truth (source code, config) and reports MATCH/DRIFT/ERROR per claim.

Core rule embedded in the design: **never treat README.md as a source of truth.** It's the artifact being checked, not something to check against. Ground truth is source code (`src/notification_service.py`, `src/rate_limiter.py`) and config (`config/rate_limit_config.yaml`).

Known drift (intentional, for the demo):
- Channels: README says email/SMS only; real `SUPPORTED_CHANNELS` includes `push`.
- Retries: README says 3 retries w/ exponential backoff (1s/2s/4s); real behavior is 2 retries, fixed 2s delay.
- Rate limit: README says 100 req/s; real config (`config/rate_limit_config.yaml`) enforces 50 req/s.

## Commands

Run everything from the repo root (`session4-demo/`).

```bash
# Run the drift check (exits non-zero if drift found — usable as a CI gate)
python3 drift_watcher.py                    # defaults to context_claims.yaml
python3 drift_watcher.py <other_claims.yaml> # check a different claims file

# Run tests
pytest                                        # all tests
pytest test_drift_watcher.py                  # drift_watcher's own tests
pytest tests/test_notification_service.py     # notification_service tests
pytest test_drift_watcher.py::test_real_claims_file_finds_exactly_three_drifts  # single test
```

No build step, no lint config present.

## Architecture

- `context_claims.yaml` — the hypothesis file. Each claim entry has a `doc_claim` (what README asserts), a `source_type` (`python_attr` imports a module and reads an attribute; `yaml_path` reads a dotted path from a YAML file), and a `check` (`equals` or `set_equals`). Add a new claim here to have `drift_watcher.py` verify another README assertion.
- `drift_watcher.py` — loads each claim, resolves the real value via `load_python_attr`/`load_yaml_path`, compares with `values_match`, and prints a MATCH/DRIFT/ERROR line per claim. Non-zero exit when any claim has drifted.
- `src/notification_service.py` — real send/retry logic; `SUPPORTED_CHANNELS`, `MAX_RETRIES`, `RETRY_DELAY_SECONDS` are the ground-truth values claims are checked against.
- `src/rate_limiter.py` — loads `config/rate_limit_config.yaml` at init; `RateLimiter.limit_for()` is the enforced per-client rate.
- `config/rate_limit_config.yaml` — actual enforced rate limit (ground truth for the `rate_limit_rps` claim).
- `CHANGELOG.md` — narrative history explaining *why* each drift happened (incident-driven changes) and confirms README was never updated. Useful context when deciding whether a DRIFT result means "fix the code" or "fix the docs."
