# Agent-Ready Problem Spec — Retail Stockout Alert
(Reference example — this is what Lab 2 should produce from context_retail_reference.md)

## Objective
Flag stores where replenishment lead time is driving recurring stockouts on
top-selling SKUs, and recommend a reorder-point adjustment for human approval.

## Allowed Tools & Data
- Read-only access to `retail_store_sku_sales_90d.csv`
- No access to the live inventory, ordering, or ERP system
- No access to any customer-level or transaction-level data

## Guardrails
- MUST NOT submit, modify, or auto-approve any purchase order
- MUST NOT write to any external or production system
- MUST print recommendations only; every recommendation requires human sign-off
- MUST NOT act on stores below the defined stockout-rate threshold (avoid alert fatigue)

## Definition of Done
A printed recommendation queue listing every store above the stockout-rate
threshold, with its region, lead time, and a one-line recommended action —
and nothing executed automatically.

## Escalation Path
If a store's stockout rate is high but its lead time is normal (i.e. the
pattern doesn't match the known root cause), the agent flags it as
"needs manual investigation" rather than guessing at a cause.
