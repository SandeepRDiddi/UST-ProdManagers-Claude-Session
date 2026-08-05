# notification-service

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
