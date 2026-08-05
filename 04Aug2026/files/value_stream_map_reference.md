# Value Stream Map — notification-service
(Reference example for Lab 2 — Map the System to the Value Stream)

## The Value Stream (Lean / DevOps Handbook framework)
A value stream is the sequence of activities an organization undertakes to
deliver value to a customer, from trigger to value received. Mapping a
system onto it means locating exactly where a technical component sits in
that chain — and what breaks in the business if that component drifts from
what everyone assumes it does.

## The Chain

| Stage | What happens | Owner | notification-service's role |
|---|---|---|---|
| 1. Order placed | Customer completes checkout | Commerce team | Triggers a notification event |
| 2. Notification triggered | Order system publishes an event | Commerce team | Consumes the event |
| 3. Notification sent | Message dispatched to customer | **notification-service** | **This system** |
| 4. Customer informed | Customer receives confirmation | Customer | Depends entirely on Stage 3 succeeding |
| 5. Trust / retention | Customer trusts the brand, orders again | Business (all teams) | Downstream of every stage above |

## Where the Context Discrepancies Create Risk

- **Channels (Email/SMS documented, Push real):** if a client-facing team believes
  only Email/SMS exist, they will underrepresent notification-service's
  capability in a proposal or a client conversation — undervaluing a stage
  of the value stream that already works.
- **Retry policy (3x exponential documented, 2x fixed real):** if a stakeholder
  is told "3 retries with exponential backoff" during a reliability
  conversation, they are being given a falsely optimistic picture of
  Stage 3 → Stage 4 reliability. The real number is what actually protects
  (or doesn't protect) Stage 4.
- **Rate limit (100 documented, 50 real):** this is the sharpest risk. If a
  demand forecast for a promotional spike is built on "100 req/s," and the
  real enforced limit is 50, Stage 3 throttles under real load — Stage 4
  fails for a meaningful slice of customers exactly when trust matters most
  (Stage 5), and nobody sees it coming because the number everyone was told
  was wrong.

## The Point of This Exercise
A Context Discrepancy Report (S4) tells you *what* is wrong. A Value Stream
Map tells you *why it matters to the business* — which is the difference
between an engineering finding and a client-ready risk statement.
