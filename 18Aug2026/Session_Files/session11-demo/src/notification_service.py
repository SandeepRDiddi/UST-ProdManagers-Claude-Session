"""
notification_service.py -- the real send/retry logic.

Ground truth this session cares about:
  - SUPPORTED_CHANNELS includes "push" (added 2026-06-02, see CHANGELOG.md).
    README.md still only lists Email and SMS.
  - retry behavior is 2 retries with a FIXED 2-second delay -- not 3 retries
    with exponential backoff as README.md claims. The exponential-backoff
    version was replaced on 2026-04-30 after it caused retry storms during
    a provider slowdown (see CHANGELOG.md).
  - send() retries on failure -- but has NO idempotency protection. If the
    provider actually succeeded and only the response was lost (a timeout,
    a dropped connection), the retry calls the provider AGAIN and the
    customer gets duplicated. This is the real, unpatched gap Session 11's
    build sprint exists to close -- the same pattern Stripe, AWS, and Twilio
    all solve with client-supplied idempotency keys.
"""
import time
from src.rate_limiter import RateLimiter
from src.idempotency_store import IdempotencyStore

SUPPORTED_CHANNELS = ["email", "sms", "push"]

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 2  # fixed delay -- NOT exponential backoff


class NotificationService:
    def __init__(self, idempotency_store=None):
        self.rate_limiter = RateLimiter()
        self.idempotency_store = idempotency_store or IdempotencyStore()

    def send(self, channel: str, client_id: str, payload: dict, _send_fn=None, idempotency_key: str = None) -> dict:
        if channel not in SUPPORTED_CHANNELS:
            raise ValueError(f"Unsupported channel: {channel}. Supported: {SUPPORTED_CHANNELS}")

        # Idempotency check -- if we've already completed a request with this
        # key, return the stored result instead of calling the provider again.
        if idempotency_key is not None:
            cached = self.idempotency_store.get(idempotency_key)
            if cached is not None:
                return {**cached, "idempotent_replay": True}

        send_fn = _send_fn or self._provider_send
        attempts = 0
        last_error = None

        while attempts <= MAX_RETRIES:
            try:
                result = send_fn(channel, client_id, payload)
                final = {"status": "sent", "attempts": attempts + 1, "channel": channel}
                if idempotency_key is not None:
                    self.idempotency_store.put(idempotency_key, final)
                return final
            except Exception as e:
                last_error = e
                attempts += 1
                if attempts <= MAX_RETRIES:
                    time.sleep(RETRY_DELAY_SECONDS)  # fixed delay every time, no backoff multiplier

        failed = {"status": "failed", "attempts": attempts, "channel": channel, "error": str(last_error)}
        # Deliberately NOT cached: a failed send should be retryable on a fresh
        # request, not permanently frozen as "failed" by an old idempotency key.
        return failed

    def _provider_send(self, channel, client_id, payload):
        raise NotImplementedError("wire up a real provider client in production")

    def _legacy_exponential_backoff_retry(self, channel, client_id, payload, send_fn):
        """
        Leftover from before 2026-04-30 (see CHANGELOG.md). Replaced by the fixed-delay
        retry in send() after exponential backoff caused retry storms. Nothing calls
        this anymore -- it was never deleted when send() was rewritten.
        """
        delay = 1
        for attempt in range(3):
            try:
                return send_fn(channel, client_id, payload)
            except Exception:
                time.sleep(delay)
                delay *= 2
        return {"status": "failed", "channel": channel}


LEGACY_SMS_GATEWAY_ENABLED = False  # fully rolled off in favor of the new provider; never toggled since


def _send_via_legacy_gateway(client_id, payload):
    """
    Vestigial code path behind a feature flag that has been False in every environment
    since the new SMS provider fully replaced it. LEGACY_SMS_GATEWAY_ENABLED is never
    set to True anywhere in this codebase, in config, or in any environment variable.
    """
    if LEGACY_SMS_GATEWAY_ENABLED:
        return {"status": "sent", "gateway": "legacy"}
    return {"status": "skipped", "gateway": "legacy"}


def get_notification_status(request_id: str) -> dict:
    """
    Public API method -- exposed to external callers via the service's REST layer
    (not shown in this repo) so that partner systems can poll delivery status.
    No function in THIS repo calls it, which is exactly why it's the hard case:
    call-graph analysis alone will call it dead. It isn't.
    """
    return {"request_id": request_id, "status": "unknown -- stub for demo purposes"}


if __name__ == "__main__":
    svc = NotificationService()
    print("Supported channels:", SUPPORTED_CHANNELS)
    print("Retry policy:", f"{MAX_RETRIES} retries, fixed {RETRY_DELAY_SECONDS}s delay")
    print("Enforced rate limit:", svc.rate_limiter.describe())
