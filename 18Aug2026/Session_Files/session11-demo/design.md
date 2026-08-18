# design.md — Idempotency-Key Support

## Approach

Add a small, swappable storage component (`IdempotencyStore`) rather than
embedding a dict directly in `NotificationService`. Two methods only:
`get(key)` and `put(key, result)`. This is the same interface shape a
Redis-backed version would expose later — the point of designing it this
way is that R4 (TTL) and a future backend swap don't require touching
`send()` again.

## Where the Check Goes

At the very top of `send()`, before the retry loop: if an `idempotency_key`
is supplied and a non-expired result exists for it, return that result
immediately (tagged `idempotent_replay: True` so callers — and tests — can
tell a replay from a fresh send). Only fall through to the real retry loop
on a cache miss.

## Where the Store Gets Written

Only on a genuinely successful send, inside the retry loop's success path —
never on a failure path. This is what makes R5 true without extra code: a
failure simply never reaches the `put()` call, so the key stays open for a
real retry later.

## What Doesn't Change

`send()`'s existing parameters and defaults stay exactly as they are.
`idempotency_key` is a new, optional, keyword-only-in-practice parameter
defaulting to `None`. Every existing caller in `tests/` and elsewhere in the
codebase continues to work with zero modification — this is what R3 is
actually testing.

## Risk Called Out Explicitly

The in-memory store does not survive a process restart and does not work
across multiple running instances of the service — in real production this
would sit behind Redis with a TTL index. Flag this as a known limitation in
your PR description, don't silently ship it as if it were production-ready
as-is.
