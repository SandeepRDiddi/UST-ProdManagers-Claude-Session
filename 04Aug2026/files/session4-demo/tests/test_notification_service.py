"""
test_notification_service.py -- these tests pass against the REAL behavior.
If README.md's claims (3 retries, exponential backoff, email/SMS only) were true,
test_retry_uses_fixed_delay_not_backoff and test_push_channel_is_supported below
would fail. They don't. This is the point of the whole demo.
"""
import time
import pytest
from src.notification_service import NotificationService, SUPPORTED_CHANNELS, MAX_RETRIES, RETRY_DELAY_SECONDS


def test_push_channel_is_supported():
    # README.md says "Email, SMS" only. This test proves push is real and supported.
    assert "push" in SUPPORTED_CHANNELS
    assert set(SUPPORTED_CHANNELS) == {"email", "sms", "push"}


def test_unsupported_channel_raises():
    svc = NotificationService()
    with pytest.raises(ValueError):
        svc.send("carrier_pigeon", "client-1", {"msg": "hi"})


def test_retry_count_is_two_not_three():
    # README.md says "up to 3 times". Real MAX_RETRIES is 2.
    assert MAX_RETRIES == 2


def test_retry_uses_fixed_delay_not_backoff(monkeypatch):
    # README.md says "exponential backoff (1s, 2s, 4s)". Real delay is a FIXED 2s every attempt.
    delays = []
    monkeypatch.setattr(time, "sleep", lambda s: delays.append(s))

    def always_fails(channel, client_id, payload):
        raise ConnectionError("provider down")

    svc = NotificationService()
    result = svc.send("email", "client-1", {"msg": "hi"}, _send_fn=always_fails)

    assert result["status"] == "failed"
    assert result["attempts"] == MAX_RETRIES + 1  # 1 initial + 2 retries = 3 attempts total
    assert delays == [RETRY_DELAY_SECONDS, RETRY_DELAY_SECONDS]  # fixed, not [1, 2, 4]


def test_successful_send_reports_channel():
    svc = NotificationService()
    result = svc.send("push", "client-1", {"msg": "hi"}, _send_fn=lambda c, cid, p: {"ok": True})
    assert result == {"status": "sent", "attempts": 1, "channel": "push"}
