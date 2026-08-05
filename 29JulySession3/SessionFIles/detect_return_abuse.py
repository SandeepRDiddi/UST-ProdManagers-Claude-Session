#!/usr/bin/env python3
"""
detect_return_abuse.py -- the Guardrails Case 1 was missing, built after the fact.

Flags (a) any auto-approved return above a dollar threshold, and (b) any
customer with a repeat-return pattern within the window -- exactly the two
checks that were never written into the original one-line ask.

Usage:
    python3 detect_return_abuse.py returns_queue.csv
"""
import sys
import pandas as pd

DOLLAR_THRESHOLD = 150
REPEAT_THRESHOLD = 3

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 detect_return_abuse.py <returns_queue_csv>")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1])

    above_threshold = df[(df.return_amount > DOLLAR_THRESHOLD) & (df.auto_approved == 1)]
    print(f"Loaded {len(df)} returns\n")
    print(f"GUARDRAIL 1 -- auto-approved above ${DOLLAR_THRESHOLD} with zero review: {len(above_threshold)}")

    repeat_counts = df.groupby("customer_id").size()
    avg_amount = df.groupby("customer_id").return_amount.mean()
    repeat_customers = repeat_counts[
        (repeat_counts >= REPEAT_THRESHOLD) & (avg_amount.reindex(repeat_counts.index) > DOLLAR_THRESHOLD)
    ].index
    repeat_returns = df[df.customer_id.isin(repeat_customers)]

    print(f"GUARDRAIL 2 -- accounts with {REPEAT_THRESHOLD}+ returns AND average return value above "
          f"${DOLLAR_THRESHOLD} (repeat pattern, not just coincidence): {len(repeat_customers)}")
    print(f"  Total $ across their returns: ${repeat_returns.return_amount.sum():,.2f}\n")

    print("Recommendation: hold any return above the dollar threshold, or from a flagged "
          "repeat-pattern account, for human review instead of auto-approving.")

if __name__ == "__main__":
    main()
