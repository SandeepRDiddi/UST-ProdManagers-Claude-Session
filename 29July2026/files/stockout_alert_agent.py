#!/usr/bin/env python3
"""
stockout_alert_agent.py -- Agent-ready stockout triage tool (Lab 2 reference build)

Scope, per agent_spec.md: this tool ONLY reads sales/inventory data and prints
a recommendation queue. It never writes to any external system and never
submits a purchase order. Every recommendation requires human approval.

Usage:
    python3 stockout_alert_agent.py retail_store_sku_sales_90d.csv
"""
import sys
import csv
from collections import defaultdict

STOCKOUT_THRESHOLD = 0.30  # flag any store above 30% stockout rate

def load_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def compute_store_stats(rows):
    totals = defaultdict(lambda: {"days": 0, "stockouts": 0, "lead_time": None, "region": None})
    for r in rows:
        s = totals[r["store_id"]]
        s["days"] += 1
        s["stockouts"] += int(r["stockout_flag"])
        s["lead_time"] = r["replenishment_lead_time_days"]
        s["region"] = r["region"]
    return totals

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 stockout_alert_agent.py <sales_csv>")
        sys.exit(1)

    rows = load_rows(sys.argv[1])
    stats = compute_store_stats(rows)

    flagged = []
    for store_id, s in stats.items():
        rate = s["stockouts"] / s["days"]
        if rate > STOCKOUT_THRESHOLD:
            flagged.append((store_id, s["region"], s["lead_time"], rate))

    flagged.sort(key=lambda x: x[3], reverse=True)

    print(f"Loaded {len(rows)} store-days across {len(stats)} stores\n")
    print("RECOMMENDATION QUEUE -- FOR HUMAN APPROVAL, NOT AUTO-EXECUTED\n")
    if not flagged:
        print("No stores above threshold.")
        return
    for store_id, region, lead_time, rate in flagged:
        print(f"  {store_id} ({region}) -- stockout rate {rate*100:.1f}% "
              f"-- lead time {lead_time} days -- RECOMMEND: reduce reorder point / expedite lead time")
    print(f"\n{len(flagged)} store(s) flagged above {STOCKOUT_THRESHOLD*100:.0f}% threshold. "
          f"No purchase orders submitted -- awaiting human sign-off.")

if __name__ == "__main__":
    main()
