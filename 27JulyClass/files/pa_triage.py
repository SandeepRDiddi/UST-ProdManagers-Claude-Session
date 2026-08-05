#!/usr/bin/env python3
"""
pa_triage.py -- Prior-Authorization Triage Assistant (demo / training tool)

Scope, by design: this tool ONLY flags procedural gaps (missing required
documentation) for fast provider follow-up. It never auto-approves or
auto-denies a clinical judgment call -- those are always routed to a human
reviewer. This split is the entire point of the demo.

Usage:
    python3 pa_triage.py prior_auth_requests_synthetic.csv
"""
import sys
import csv
from collections import Counter

def load_requests(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))

def triage(rows):
    procedural, clinical_review, approved = [], [], []
    for r in rows:
        status = r["final_status"]
        reason = r["denial_reason_category"]
        if status == "approved":
            approved.append(r)
        elif reason == "missing_documentation":
            procedural.append(r)
        elif reason == "clinical_criteria_not_met":
            clinical_review.append(r)
    return procedural, clinical_review, approved

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pa_triage.py <requests_csv>")
        sys.exit(1)

    rows = load_requests(sys.argv[1])
    procedural, clinical_review, approved = triage(rows)

    print(f"Loaded {len(rows)} prior-authorization requests\n")
    print(f"  Approved:                          {len(approved)}")
    print(f"  Flagged -- procedural (fast-track): {len(procedural)}")
    print(f"  Routed  -- clinical judgment (human review): {len(clinical_review)}\n")

    if procedural:
        print("PROCEDURAL QUEUE -- missing documentation, safe to auto-flag:")
        by_cat = Counter(r["category"] for r in procedural)
        for cat, n in by_cat.most_common():
            print(f"  - {cat}: {n} request(s)")
        print("  Sample:")
        for r in procedural[:3]:
            missing = int(r["documentation_required_count"]) - int(r["documentation_submitted_count"])
            print(f"    {r['request_id']} ({r['procedure_desc']}): missing {missing} required document(s)")
        print()

    if clinical_review:
        print("CLINICAL REVIEW QUEUE -- do NOT auto-decide, route to reviewer:")
        by_cat = Counter(r["category"] for r in clinical_review)
        for cat, n in by_cat.most_common():
            print(f"  - {cat}: {n} request(s)")

if __name__ == "__main__":
    main()
