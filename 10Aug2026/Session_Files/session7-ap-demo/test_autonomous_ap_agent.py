"""
test_autonomous_ap_agent.py -- proves the governance guarantees the agent claims,
against the real dataset. This is the exact thing a CIO's risk team would check.
"""
import csv


def load_rows(path="ap_invoices_fy26.csv"):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def test_no_duplicate_suspect_ever_auto_approved():
    rows = load_rows()
    violations = [r for r in rows if r["is_duplicate_suspect"] == "True" and int(r["autonomy_tier"]) >= 3]
    assert violations == [], f"Governance violation: {len(violations)} duplicate-suspect invoices auto-approved"


def test_no_missing_po_ever_auto_approved():
    rows = load_rows()
    violations = [r for r in rows if r["po_match_status"] == "no_po" and int(r["autonomy_tier"]) >= 3]
    assert violations == [], f"Governance violation: {len(violations)} no-PO invoices auto-approved"


def test_no_invoice_over_250k_ever_auto_approved():
    rows = load_rows()
    violations = [r for r in rows if float(r["amount"]) > 250000 and int(r["autonomy_tier"]) >= 3]
    assert violations == [], f"Governance violation: {len(violations)} invoices over $250k auto-approved"


def test_tier4_only_exact_match_under_10k():
    rows = load_rows()
    violations = [
        r for r in rows
        if int(r["autonomy_tier"]) == 4
        and not (r["po_match_status"] == "matched_exact" and float(r["amount"]) <= 10000)
    ]
    assert violations == [], f"Tier 4 rule violated by {len(violations)} invoices"


def test_new_vendor_never_above_tier2():
    rows = load_rows()
    violations = [
        r for r in rows
        if int(r["vendor_tenure_months"]) < 6 and int(r["autonomy_tier"]) >= 3
    ]
    assert violations == [], f"New-vendor rule violated by {len(violations)} invoices"


if __name__ == "__main__":
    import sys
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests)-failed}/{len(tests)} governance guarantees verified")
    sys.exit(1 if failed else 0)
