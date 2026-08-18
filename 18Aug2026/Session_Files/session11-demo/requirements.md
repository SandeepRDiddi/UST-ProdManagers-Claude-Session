# requirements.md — Idempotency-Key Support for notification-service

## Background (why this matters — read before you spec anything)

`NotificationService.send()` retries up to 2 times on failure, with a fixed
2-second delay. This is correct behavior for one failure mode (the provider
genuinely didn't receive the request) and actively harmful for another: if
the provider *did* process the request but the success response was lost —
a timeout, a dropped connection, a slow network — the retry calls the
provider again, and the customer gets the same notification twice.

This is not a hypothetical. It's the single most common reliability bug in
distributed systems that talk to external providers, and it's why every
serious payments and messaging API — Stripe, AWS, Twilio — makes the client
supply an **idempotency key**: a string the client generates once per
logical request, so the server can recognize "I've already done this" and
return the prior result instead of repeating the side effect.

## In Scope

Add optional idempotency-key support to `NotificationService.send()`.

## Out of Scope

- Concurrency safety (two threads submitting the same key at the exact same
  instant) — real and important, but not required for this sprint. Note it
  as a follow-up if you spot it.
- Swapping the storage backend to Redis — the interface should make this
  possible later without touching `send()`, but implementing it now is out
  of scope.

## Requirements (EARS format)

**R1.** WHEN a request is submitted with an `idempotency_key` that has not
been seen before, the system SHALL process it normally and store the result
keyed by that `idempotency_key`.

**R2.** WHEN a request is submitted with an `idempotency_key` that matches a
previously *completed* request, the system SHALL return the stored result
without calling the provider again.

**R3.** WHEN a request is submitted without an `idempotency_key`, the system
SHALL process it exactly as it does today — no behavior change, no
regression for existing callers.

**R4.** WHEN a stored idempotency result is older than a configurable TTL
(default 24 hours), the system SHALL treat a new request with that key as
unseen, not return stale cached data indefinitely.

**R5.** IF a request fails after retries are exhausted, THEN the system
SHALL NOT cache the failure under that key — a fresh request with the same
key later must be allowed to try again, not be permanently frozen as failed.

## Definition of Done

- All 5 requirements above have a passing automated test.
- All existing tests in `tests/` still pass unmodified — this is an
  additive feature, not a rewrite.
- `send()`'s existing call signature still works with no `idempotency_key`
  argument at all — full backward compatibility.
