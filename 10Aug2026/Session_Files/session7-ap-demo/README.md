# Session 7 — Autonomous AP Demo

Production-shaped demo: a tiered-autonomy invoice-to-pay agent for a Finance
use case, built for a CIO business-case narrative. Everything here is real
and re-runnable — no numbers in the session materials are invented.

## Files

- `ap_invoices_fy26.csv` — 1,800 synthetic invoices, one realistic month.
  Includes the `autonomy_tier` column already computed.
- `gen_ap_invoices.py` — regenerates the dataset and prints the tier
  distribution and ROI numbers from scratch (seeded, reproducible).
- `autonomous_ap_agent.py` — the tiered-autonomy processing agent. Reads the
  CSV, classifies (already-classified in this build), and writes a governance
  audit log for every Tier 3/4 decision.
- `test_autonomous_ap_agent.py` — 5 governance guarantee tests, run against
  the real data. This is what a CIO's risk/compliance team would actually ask
  to see before approving Tier 3/4 autonomy.
- `cio_business_case.html` — the finished CIO-ready dashboard. Open directly
  in a browser, no server needed.

## Quickstart

```
python3 autonomous_ap_agent.py ap_invoices_fy26.csv
python3 test_autonomous_ap_agent.py
open cio_business_case.html
```

## The Numbers (verified, not projected)

- 1,800 invoices/month · 61.6% fully touchless (Tier 4)
- $25,200/mo manual baseline → $5,586/mo agent operational cost
- $19,614/mo gross savings · $17,214/mo net after governance overhead
- $38,000 one-time build · 2.2-month payback · $168,568 Year 1 net benefit
- 5/5 governance guarantees pass against the real dataset

## Autonomy Tiers

| Tier | Label | Rule |
|---|---|---|
| 4 | Full autonomy | Exact PO match, established vendor (6mo+), ≤ $10,000 |
| 3 | Conditional autonomy | PO matched within 5% variance, established vendor, ≤ $50,000 |
| 2 | Assisted | New vendor (<6mo), or PO mismatch beyond Tier 3, or $50k–$250k |
| 1 | Manual only | No PO, duplicate-suspect, or > $250,000 |
