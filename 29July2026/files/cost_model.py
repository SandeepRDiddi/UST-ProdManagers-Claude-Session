#!/usr/bin/env python3
"""
cost_model.py -- Cost of Problem vs Cost of Existence (Lab 3 reference build)

Scales the VERIFIED procedural/clinical split from the 70-request sample
(prior_auth_requests_synthetic.csv, S1) to an illustrative monthly network
volume. All dollar figures below are TRAINING ASSUMPTIONS -- replace with
real client numbers before using this outside the classroom.

Usage:
    python3 cost_model.py
"""

# ---- verified sample split (70 requests, S1 dataset) ----
SAMPLE = {"approved": 16, "procedural": 32, "clinical": 22}
SAMPLE_TOTAL = sum(SAMPLE.values())

# ---- illustrative assumptions (state these out loud in class) ----
MONTHLY_VOLUME = 1200
HOURLY_RATE = 45          # fully-loaded staff rate, $/hr
HOURS_BEFORE = 1.5        # rework hours per procedural denial, today
HOURS_AFTER = 0.9         # rework hours per procedural denial, with the agent
BUILD_HOURS = 120
BUILD_RATE = 85           # $/hr engineering rate
API_COST_PER_REQUEST = 0.02
GOVERNANCE_HOURS_MONTHLY = 8

def scale_volume():
    scaled = {k: round(v / SAMPLE_TOTAL * MONTHLY_VOLUME) for k, v in SAMPLE.items()}
    drift = MONTHLY_VOLUME - sum(scaled.values())
    scaled["procedural"] += drift  # absorb rounding drift in the largest bucket
    return scaled

def main():
    scaled = scale_volume()
    print("Monthly volume (scaled from verified sample proportions):")
    for k, v in scaled.items():
        print(f"  {k}: {v}")

    cop_monthly = scaled["procedural"] * HOURS_BEFORE * HOURLY_RATE
    print(f"\nCost of Problem (monthly, procedural rework only): ${cop_monthly:,.0f}")

    build_cost = BUILD_HOURS * BUILD_RATE
    coe_monthly = scaled["procedural"] * 0 + MONTHLY_VOLUME * API_COST_PER_REQUEST + GOVERNANCE_HOURS_MONTHLY * BUILD_RATE
    print(f"Cost of Existence -- one-time build: ${build_cost:,.0f}")
    print(f"Cost of Existence -- steady-state monthly: ${coe_monthly:,.2f}")

    saved_hours = HOURS_BEFORE - HOURS_AFTER
    gross_savings = scaled["procedural"] * saved_hours * HOURLY_RATE
    net_benefit = gross_savings - coe_monthly
    print(f"\nGross monthly savings from reduced rework: ${gross_savings:,.0f}")
    print(f"Net monthly benefit (after Cost of Existence): ${net_benefit:,.0f}")

    payback_months = build_cost / net_benefit
    print(f"Payback period on build cost: {payback_months:.2f} months "
          f"(~{payback_months*4.345:.1f} weeks)")

if __name__ == "__main__":
    main()
