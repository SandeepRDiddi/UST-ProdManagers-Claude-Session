#!/usr/bin/env python3
"""
detect_duplicate_payments.py -- the Guardrail Case 4 was missing, built after the fact.

Flags any pair of PAID invoices from the same vendor, same amount, same PO,
within a configurable date window -- exactly the pattern that slipped through
in the incident. In production, this check would run BEFORE payment, flagging
the second invoice for human review instead of auto-paying it.

Usage:
    python3 detect_duplicate_payments.py invoice_queue.csv
"""
import sys
import pandas as pd

DATE_WINDOW_DAYS = 14  # flag same vendor+amount+PO invoices within this many days of each other

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 detect_duplicate_payments.py <invoice_queue_csv>")
        sys.exit(1)

    df = pd.read_csv(sys.argv[1], parse_dates=["invoice_date"])
    paid = df[df.payment_status == "paid"].copy()

    flagged_pairs = []
    for (vendor, po, amount), group in paid.groupby(["vendor_id", "po_number", "amount"]):
        if len(group) < 2:
            continue
        group = group.sort_values("invoice_date")
        rows = group.to_dict("records")
        for i in range(len(rows) - 1):
            gap = (rows[i+1]["invoice_date"] - rows[i]["invoice_date"]).days
            if gap <= DATE_WINDOW_DAYS:
                flagged_pairs.append((rows[i], rows[i+1], gap))

    print(f"Loaded {len(df)} invoices ({len(paid)} paid)\n")
    print(f"DUPLICATE-PAYMENT GUARDRAIL -- would have flagged {len(flagged_pairs)} pair(s) for human review:\n")
    total_exposure = 0
    for original, duplicate, gap in flagged_pairs:
        total_exposure += duplicate["amount"]
        print(f"  {original['vendor_name']}: {original['invoice_id']} (${original['amount']:,.2f}, "
              f"{original['invoice_date'].date()}) and {duplicate['invoice_id']} "
              f"(${duplicate['amount']:,.2f}, {duplicate['invoice_date'].date()}) -- {gap} days apart")
    print(f"\nTotal exposure this guardrail would have caught: ${total_exposure:,.2f}")
    print("Recommendation: hold the second invoice in each pair for human review -- do not auto-pay.")

if __name__ == "__main__":
    main()
