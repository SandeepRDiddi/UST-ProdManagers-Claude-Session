# tasks.md — Idempotency-Key Support

Atomic, independently testable units. Recommended build order:

1. **Create `IdempotencyStore`** — `get(key)` returns `None` on miss or
   expiry, `put(key, result)` stores with a timestamp. Unit-testable with no
   dependency on `NotificationService` at all.
2. **Wire `IdempotencyStore` into `NotificationService.__init__`** — accept
   an optional injected store (for testability), default to a real one.
3. **Add the idempotency check at the top of `send()`** — cache hit returns
   immediately, tagged `idempotent_replay: True`.
4. **Add the cache write on the success path only** — inside the retry
   loop, right where a successful result is currently returned.
5. **Write the 5 tests, one per requirement (R1–R5)** — this is the
   Definition of Done, not an afterthought. Write these before you consider
   the feature finished, not after.
6. **Run the full existing suite** — confirm zero regressions before
   calling this done.
