# notification-service

> **Session 11 note:** `requirements.md`, `design.md`, and `tasks.md` are the
> real SDD brief for this session's build sprint — adding idempotency-key
> support to `send()` so a network retry can't cause a duplicate customer
> notification. `src/idempotency_store.py` and the updated `send()` are the
> reference implementation (5/5 new requirements tested, 13/13 total tests
> passing). Build your own version first with Claude Code before comparing
> against it. (Yes, the README below is still the deliberately-stale one
> from Session 4/6 — that's intentional, don't fix it.)

Sends customer notifications on behalf of downstream services (order confirmations,
shipping updates, payment failures).

## Channels Supported
- Email
- SMS

## Reliability
Failed sends are automatically retried up to **3 times**, using **exponential backoff**
(1s, 2s, 4s) to avoid overwhelming downstream providers during an outage.

## Rate Limiting
Each client is rate-limited to **100 requests per second** to protect shared
provider quota.

## Owning Team
Platform Messaging Team — #notifications-support

## Getting Started
```
pip install -r requirements.txt
python src/notification_service.py
```

See `docs/architecture.md` for the full design (last reviewed: last year's
onboarding cycle — ask in #notifications-support if anything looks out of date).
