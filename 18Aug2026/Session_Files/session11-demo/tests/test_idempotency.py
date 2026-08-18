"""
test_idempotency.py -- proves the idempotency-key feature actually does its job:
a retried request with the same key does NOT call the provider twice, and a
request with a new (or no) key is unaffected.
"""
import time
import pytest
from src.notification_service import NotificationService


def test_no_idempotency_key_behaves_exactly_as_before():
    svc = NotificationService()
    calls = []
    def track_call(c, cid, p):
        calls.append(1)
        return {"ok": True}
    result = svc.send("email", "client-1", {"msg": "hi"}, _send_fn=track_call)
    assert result["status"] == "sent"
    assert len(calls) == 1
    assert "idempotent_replay" not in result


def test_same_idempotency_key_calls_provider_only_once():
    svc = NotificationService()
    calls = []
    def track_call(c, cid, p):
        calls.append(1)
        return {"ok": True}

    first = svc.send("email", "client-1", {"msg": "hi"}, _send_fn=track_call, idempotency_key="order-123")
    second = svc.send("email", "client-1", {"msg": "hi"}, _send_fn=track_call, idempotency_key="order-123")

    assert len(calls) == 1  # the actual bug fix: provider only called once
    assert first["status"] == "sent"
    assert second["status"] == "sent"
    assert second["idempotent_replay"] is True


def test_different_idempotency_keys_both_send():
    svc = NotificationService()
    calls = []
    def track_call(c, cid, p):
        calls.append(1)
        return {"ok": True}

    svc.send("email", "client-1", {"msg": "hi"}, _send_fn=track_call, idempotency_key="order-1")
    svc.send("email", "client-1", {"msg": "hi"}, _send_fn=track_call, idempotency_key="order-2")

    assert len(calls) == 2  # different keys are genuinely different requests


def test_expired_idempotency_key_sends_again():
    svc = NotificationService()
    svc.idempotency_store.ttl_seconds = 0.05  # force fast expiry for the test
    calls = []
    def track_call(c, cid, p):
        calls.append(1)
        return {"ok": True}

    svc.send("email", "client-1", {"msg": "hi"}, _send_fn=track_call, idempotency_key="order-9")
    time.sleep(0.1)
    svc.send("email", "client-1", {"msg": "hi"}, _send_fn=track_call, idempotency_key="order-9")

    assert len(calls) == 2  # key expired -- correctly treated as a new request


def test_failed_send_is_not_cached_and_can_retry_fresh():
    svc = NotificationService()

    def always_fails(c, cid, p):
        raise ConnectionError("provider down")

    result = svc.send("email", "client-1", {"msg": "hi"}, _send_fn=always_fails, idempotency_key="order-5")
    assert result["status"] == "failed"

    calls = []
    def now_succeeds(c, cid, p):
        calls.append(1)
        return {"ok": True}
    retry = svc.send("email", "client-1", {"msg": "hi"}, _send_fn=now_succeeds, idempotency_key="order-5")
    assert retry["status"] == "sent"  # a failed attempt didn't permanently poison the key
    assert len(calls) == 1
