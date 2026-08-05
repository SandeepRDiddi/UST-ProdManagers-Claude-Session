# Learning Project Lumen — Instructor Walkthrough

## Goal

Teach one idea: **documentation drifts out of sync with reality, and code/config/tests are
the only sources you can trust.** Project Lumen is a small, deliberately-rigged codebase
where the README describes a version of the service that no longer exists. Students will
discover this themselves by investigating, not by being told.

Estimated time: 30–45 minutes for a guided session, 15–20 minutes if run as a quick drill.

---

## Setup

```bash
cd files/project-lumen
pip install pyyaml pytest
```

(There's no `requirements.txt` in the repo — that's a real gap, not an intentional lesson.
Worth pointing out if a sharp student notices the README references one.)

---

## Step 1 — Read the README first (don't correct it yet)

Have students read `README.md` cold and write down three facts:
1. What channels does the service support?
2. How many retries, with what delay strategy?
3. What's the rate limit per client?

Expected answers from the README: **Email/SMS**, **3 retries with exponential backoff
(1s/2s/4s)**, **100 req/s**.

Tell them: hold onto these answers, we're about to check if they're true.

---

## Step 2 — Read the CHANGELOG

Have students open `CHANGELOG.md` and read top to bottom (newest first).

Ask: does anything here contradict what the README said?

They should notice three entries, each ending in **"README.md not updated"**:
- 2026-06-02 — added `push` channel
- 2026-05-14 — rate limit dropped 100 → 50 req/s
- 2026-04-30 — retry strategy changed from exponential backoff to fixed 2s delay, 2 retries

At this point students should already suspect the README is stale. Don't confirm yet —
send them to the code.

---

## Step 3 — Verify against the actual code

Point them at three files, in this order:

1. **`src/notification_service.py`** — look at `SUPPORTED_CHANNELS`, `MAX_RETRIES`,
   `RETRY_DELAY_SECONDS`. Ask: does this match the README or the CHANGELOG?
2. **`config/rate_limit_config.yaml`** — the real enforced rate limit, loaded at runtime.
3. **`src/rate_limiter.py`** — shows *how* the config is loaded, proving the 50 req/s
   value isn't hardcoded fiction — it's read from config at startup.

Each of these files has a comment at the top explicitly stating what's real and what the
README gets wrong. Let students find that themselves rather than reading it out loud —
it lands better as a discovery than a lecture.

---

## Step 4 — Run the tests

```bash
python -m pytest tests/ -v
```

All tests pass. Walk through what each one proves:

- `test_push_channel_is_supported` — README says Email/SMS only; test proves `push` is real.
- `test_retry_count_is_two_not_three` — README says 3 retries; test proves it's 2.
- `test_retry_uses_fixed_delay_not_backoff` — README says exponential backoff (1s/2s/4s);
  test proves fixed 2s delay every time, and asserts the recorded sleep calls are
  `[2, 2]`, not `[1, 2, 4]`.

This is the payoff moment: **the tests are written specifically to fail if the README
were true, and they don't fail.** That's the whole demo in one `pytest` run.

---

## Step 5 — Discuss why the drift happened

Read `CHANGELOG.md` again, slower. Each change had a real trigger:
- **Push channel**: a feature request from the mobile team.
- **Rate limit cut 100→50**: a production incident (provider quota exhaustion during a
  traffic spike).
- **Retry strategy change**: exponential backoff was *making an outage worse* — multiple
  instances backed off in sync, then retried in sync, creating retry storms. Fixed delay
  was the fix.

Point to make: engineers fixed the code under pressure (an incident, a feature request)
and updated tests + config same day — because CI would fail otherwise. Nobody's job was
"update the README," so it silently rotted. This is normal, not a moral failing — it's
why the exercise matters.

---

## Step 6 — The transferable lesson

Ask the class: **if you (or an AI assistant) were asked "what's the rate limit on this
service?", where would you look, and in what order?**

Correct hierarchy, most to least trustworthy:
1. **Code that runs** (`notification_service.py`, `rate_limiter.py`) — can't lie, it's
   what executes.
2. **Config it loads at runtime** (`rate_limit_config.yaml`) — same reasoning.
3. **Tests** — trustworthy *if* they're actually run in CI and passing; they encode
   intended behavior and tend to get updated alongside code.
4. **CHANGELOG** — useful for *why* and *when*, but still prose someone could forget to write.
5. **README / docs** — least trustworthy. Treat as a hypothesis to verify, not a fact.

This generalizes past this repo: any time you or an AI tool answers a question about a
system by summarizing its README without checking the code, you risk repeating stale
claims exactly like the ones in this repo.

---

## Optional extension exercises

- Have students **fix the README** to match reality, then diff it against `CHANGELOG.md`
  to confirm every entry is now reflected.
- Ask students to write a **pre-commit hook or CI check** that fails a PR if `src/` or
  `config/` changes without a corresponding `README.md` change in the same commit —
  turns the lesson into a concrete engineering practice.
- Ask: what's the risk of trusting an AI coding assistant that only reads `README.md`
  when asked to explain or modify this service? (It would confidently repeat the wrong
  retry count, wrong channel list, wrong rate limit.)

---

## Quick reference — ground truth vs. README

| Fact | README claims | Actually true | Source of truth |
|---|---|---|---|
| Channels | Email, SMS | Email, SMS, **Push** | `src/notification_service.py` |
| Retries | 3, exponential backoff (1s/2s/4s) | **2, fixed 2s delay** | `src/notification_service.py` |
| Rate limit | 100 req/s | **50 req/s** | `config/rate_limit_config.yaml` |
