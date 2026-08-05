# Business-Context Artifact — Retail Stockout Problem
(Reference example — this is what Lab 1 should produce. Treat blanks as the
parts a real team would fill in with their own numbers.)

## 1. Problem Statement
Top-selling SKUs stock out repeatedly at a subset of stores during peak
weekends, even though total network inventory is healthy. Verified in S1:
West-region stores stock out on 45.5% of store-days vs. 14.5% elsewhere;
stockout rate correlates with replenishment lead time at r = 0.98, not with
demand variance (r = 0.07).

## 2. Stakeholders & Owners
- Problem owner: Regional Retail Operations Lead
- Affected: Store managers (lost sales, manual Excel tracking), Merchandising
  (blamed for "wrong" allocation), Customers (can't find in-stock items)
- Decision-maker for any automation: VP of Supply Chain

## 3. Current Workaround
Store managers export weekly sales to Excel every Monday and eyeball which
SKUs look low. No standardized escalation when a store is chronically behind.

## 4. Data Sources & Fields Available
`retail_store_sku_sales_90d.csv` — date, store_id, region, sku_id,
sku_category, units_demand, units_sold, units_on_hand_eod, stockout_flag,
replenishment_lead_time_days, demand_variance_tier. 90 days, 15 stores, 8 SKUs.

## 5. Constraints
- No write access to the live inventory or ordering system
- No real customer or transaction-level PII in this dataset
- Any reorder-point change must be approved by a human before it takes effect

## 6. Success Metric
Reduce West-region stockout rate from 45.5% to under 20% within one quarter,
without increasing network-wide inventory dollars.

## 7. Out of Scope
- Forecasting model redesign
- SKU assortment decisions
- Anything touching the live ordering/ERP system directly
