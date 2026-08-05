# Changelog

## 2026-06-02
- Added `push` as a supported notification channel (mobile team requested it for
  order-status alerts). Code and tests updated. **README.md not updated.**

## 2026-05-14
- Lowered enforced rate limit from 100 req/s to 50 req/s per client after a
  provider quota incident during a traffic spike. Config and code updated same day.
  **README.md not updated.**

## 2026-04-30
- Replaced exponential-backoff retry (3 attempts: 1s/2s/4s) with a simpler fixed-delay
  retry (2 attempts, flat 2s) after exponential backoff was found to cause retry
  storms during a provider slowdown -- multiple instances backing off in sync then
  retrying in sync made the problem worse, not better. Code and tests updated.
  **README.md not updated.**

## 2026-02-01
- Initial version. README.md accurate as of this date: 2 channels (email, SMS),
  3 retries with exponential backoff, 100 req/s rate limit.
