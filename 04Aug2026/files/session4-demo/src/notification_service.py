"""
notification_service.py -- the real send/retry logic.

Ground truth this session cares about:
  - SUPPORTED_CHANNELS includes "push" (added 2026-06-02, see CHANGELOG.md).
    README.md still only lists Email and SMS.
  - retry behavior is 2 retries with a FIXED 2-second delay -- not 3 retries
    with exponential backoff as README.md claims. The exponential-backoff
    version was replaced on 2026-04-30 after it caused retry storms during
    a provider slowdown (see CHANGELOG.md).
"""
import time
from src.rate_limiter import RateLimiter

SUPPORTED_CHANNELS = ["email", "sms", "push"]

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2  # fixed delay -- NOT exponential backoff


class NotificationService:
    def __init__(self):
        self.rate_limiter = RateLimiter()

    def send(self, channel: str, client_id: str, payload: dict, _send_fn=None) -> dict:
        if channel not in SUPPORTED_CHANNELS:
            raise ValueError(f"Unsupported channel: {channel}. Supported: {SUPPORTED_CHANNELS}")

        send_fn = _send_fn or self._provider_send
        attempts = 0
        last_error = None

        while attempts <= MAX_RETRIES:
            try:
                result = send_fn(channel, client_id, payload)
                return {"status": "sent", "attempts": attempts + 1, "channel": channel}
            except Exception as e:
                last_error = e
                attempts += 1
                if attempts <= MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)  # fixed delay every time, no backoff multiplier

        return {"status": "failed", "attempts": attempts, "channel": channel, "error": str(last_error)}

    def _provider_send(self, channel, client_id, payload):
        raise NotImplementedError("wire up a real provider client in production")


if __name__ == "__main__":
    svc = NotificationService()
    print("Supported channels:", SUPPORTED_CHANNELS)
    print("Retry policy:", f"{MAX_RETRIES} retries, fixed {RETRY_DELAY_SECONDS}s delay")
    print("Enforced rate limit:", svc.rate_limiter.describe())
