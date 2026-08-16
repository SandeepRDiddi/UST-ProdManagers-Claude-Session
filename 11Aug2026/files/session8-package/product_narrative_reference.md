# Product Narrative — Autonomous Accounts Payable
(Reference example for Lab 1 — Draft the Full Product Narrative)
Structured with SCQA. This is complete prose, the way it would actually be
read aloud or handed to a panel — not bullet points.

---

**Situation.** Accounts Payable at [Client] processes roughly 1,800 invoices
a month. Every one of them is reviewed manually, regardless of how routine
or how risky it actually is. That process costs approximately $25,200 a
month today, at a flat $14 per invoice whether the invoice is a $200
recurring subscription or a $200,000 capital purchase.

**Complication.** That flat-cost, flat-scrutiny model has two problems, and
only one of them shows up on a budget line. The first is obvious: manual
review capacity doesn't scale linearly with invoice volume, so as the
business grows, either headcount grows with it or turnaround time degrades.
The second is less visible but more important: manual review fatigue —
reviewers moving quickly through high volumes of low-risk invoices — is
exactly where duplicate-payment and fraud exposure actually lives. Nobody
has measured that exposure, because nobody has had a reason to look closely
at 1,800 invoices that all get the same level of scrutiny.

**Question.** How do we materially reduce processing cost and turnaround
time without increasing the very risk that manual review exists to control
— and without asking anyone to trust a system that can't show its work?

**Answer.** A tiered-autonomy agent that automates only where risk is
provably low, and hands off everything else to a human, by design. Every
invoice is classified into one of four tiers based on hard, testable rules:
exact PO match and an established vendor relationship earns full autonomy
below $10,000; a small matched variance earns conditional autonomy below
$50,000, with every decision logged and a live sample routed for human
audit; anything involving a new vendor, a larger mismatch, or a mid-size
dollar amount goes to a human with the agent's recommendation attached; and
anything involving a missing PO, a suspected duplicate, or an amount above
$250,000 gets no automation at all — full manual review, exactly as today.

Applied to a real month of invoice data, this means 61.6% of volume clears
with zero human touch, 16.6% clears with a logged, audited decision, and
21.9% still goes to a person — either with help or entirely on their own.
Processing cost drops from $25,200 a month to $5,586 a month in direct
operational cost. After accounting for governance overhead — the audit
tooling and review time the higher tiers require — the net benefit is
$17,214 a month, which pays back the $38,000 build cost in 2.2 months.

None of these numbers are projections. They come from actually running the
classification rules and the governance test suite against a real month of
invoice data, and printing the result.
