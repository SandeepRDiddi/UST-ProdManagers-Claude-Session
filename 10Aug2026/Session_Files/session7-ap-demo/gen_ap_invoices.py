import numpy as np, pandas as pd

rng = np.random.default_rng(77)

N_VENDORS = 220
N_INVOICES = 1800

vendors = pd.DataFrame({
    "vendor_id": [f"V{1000+i}" for i in range(N_VENDORS)],
    "vendor_tenure_months": rng.integers(1, 96, N_VENDORS),
})

rows = []
base_date = pd.Timestamp("2026-06-01")

for i in range(N_INVOICES):
    v = vendors.iloc[rng.integers(0, N_VENDORS)]
    # amount: lognormal, skewed toward small/routine invoices with a long tail
    amount = round(float(np.exp(rng.normal(7.8, 1.35))), 2)   # median ~$2,400, long tail into six figures
    amount = min(amount, 650000)

    po_roll = rng.random()
    if po_roll < 0.78:
        po_match_status = "matched_exact"
        variance_pct = 0.0
    elif po_roll < 0.90:
        po_match_status = "matched_variance"
        variance_pct = round(float(rng.uniform(0.5, 9.0)), 1)
    else:
        po_match_status = "no_po"
        variance_pct = None

    is_duplicate_suspect = rng.random() < 0.015
    invoice_date = base_date + pd.Timedelta(days=int(rng.integers(0, 30)))

    rows.append({
        "invoice_id": f"AP-{600000+i}",
        "vendor_id": v.vendor_id,
        "vendor_tenure_months": int(v.vendor_tenure_months),
        "amount": amount,
        "invoice_date": invoice_date.strftime("%Y-%m-%d"),
        "po_match_status": po_match_status,
        "variance_pct": variance_pct,
        "is_duplicate_suspect": bool(is_duplicate_suspect),
    })

df = pd.DataFrame(rows)


def classify_tier(row):
    """
    Tiered-autonomy business rule (SAE-style autonomy levels applied to AP):
      Tier 4 -- full autonomy: exact PO match, established vendor, <= $10,000, no duplicate flag
      Tier 3 -- conditional autonomy: PO matched within 5% variance, established vendor, <= $50,000
      Tier 2 -- assisted: new vendor (<6mo), or PO mismatch beyond Tier 3, or $50k-$250k
      Tier 1 -- manual only: no PO, duplicate-suspect, or > $250,000
    """
    if row.is_duplicate_suspect or row.po_match_status == "no_po" or row.amount > 250000:
        return 1
    if row.vendor_tenure_months < 6:
        return 2
    if row.po_match_status == "matched_exact" and row.amount <= 10000:
        return 4
    if row.po_match_status in ("matched_exact", "matched_variance") and (row.variance_pct or 0) <= 5.0 and row.amount <= 50000:
        return 3
    return 2


df["autonomy_tier"] = df.apply(classify_tier, axis=1)

# ---- cost model: verified, stated assumptions ----
MANUAL_COST_PER_INVOICE = 14.00     # typical fully-manual AP processing cost assumption -- stated, not claimed as sourced fact
TIER_COST = {4: 0.50, 3: 2.00, 2: 8.00, 1: 14.00}

df["cost_manual_baseline"] = MANUAL_COST_PER_INVOICE
df["cost_with_agent"] = df["autonomy_tier"].map(TIER_COST)

df.to_csv("/mnt/user-data/outputs/ap_invoices_fy26.csv", index=False)

# ---- verification ----
print(f"Total invoices: {len(df)}")
print("\nTier distribution:")
tier_counts = df.autonomy_tier.value_counts().sort_index(ascending=False)
for tier, count in tier_counts.items():
    pct = count / len(df) * 100
    print(f"  Tier {tier}: {count} invoices ({pct:.1f}%)")

total_manual_cost = df.cost_manual_baseline.sum()
total_agent_cost = df.cost_with_agent.sum()
monthly_savings = total_manual_cost - total_agent_cost
pct_savings = monthly_savings / total_manual_cost * 100

print(f"\nMonthly cost, fully manual baseline: ${total_manual_cost:,.2f}")
print(f"Monthly cost, with tiered-autonomy agent: ${total_agent_cost:,.2f}")
print(f"Monthly savings: ${monthly_savings:,.2f} ({pct_savings:.1f}%)")
print(f"Annualized savings: ${monthly_savings*12:,.2f}")

touchless_pct = (df.autonomy_tier == 4).sum() / len(df) * 100
print(f"\nFully touchless (Tier 4) share of volume: {touchless_pct:.1f}%")
