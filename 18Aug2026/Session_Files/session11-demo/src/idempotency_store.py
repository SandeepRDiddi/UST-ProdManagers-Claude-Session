"""
idempotency_store.py -- stores completed-request results keyed by client-supplied
idempotency key, with a TTL so keys don't live forever.

Classroom simplification: in-memory dict. Real production services (this is
the same pattern Stripe, AWS, and Twilio all use publicly) back this with
Redis or a database with a TTL index, because an in-memory store doesn't
survive a process restart or work across multiple service instances. The
interface below (get/put) is deliberately the same shape either way, so
swapping the backend later doesn't touch NotificationService at all.
"""
import time


class IdempotencyStore:
    def __init__(self, ttl_seconds: int = 86400):  # 24-hour default window
        self.ttl_seconds = ttl_seconds
        self._store = {}  # key -> (result_dict, stored_at_timestamp)

    def get(self, key: str):
        entry = self._store.get(key)
        if entry is None:
            return None
        result, stored_at = entry
        if time.time() - stored_at > self.ttl_seconds:
            del self._store[key]  # expired -- treat as never seen
            return None
        return result

    def put(self, key: str, result: dict):
        self._store[key] = (result, time.time())
