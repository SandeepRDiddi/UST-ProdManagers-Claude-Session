#!/usr/bin/env python3
"""
analyze_ci_incident.py -- reconstructs the Case 3 postmortem evidence directly
from ci_test_history.csv and ci_incident_record.csv. This is the script the
"weekly audit" corrective action describes: find every test an agent silently
disabled, and check whether any of them line up with a later production incident.

Usage:
    python3 analyze_ci_incident.py ci_test_history.csv ci_incident_record.csv
"""
import sys
import pandas as pd

def build_pass_rate(log, day):
    d = log[log.day == day]
    fails_per_run = d[d.status == "fail"].groupby("run_id").size()
    runs = d.run_id.unique()
    passing = sum(1 for r in runs if fails_per_run.get(r, 0) == 0)
    return passing / len(runs)

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 analyze_ci_incident.py <ci_test_history_csv> <ci_incident_record_csv>")
        sys.exit(1)

    log = pd.read_csv(sys.argv[1])
    incident = pd.read_csv(sys.argv[2])

    print("=== CI Pass-Rate Trend ===")
    for day in sorted(log.day.unique()):
        print(f"  Day {day:>2}: {build_pass_rate(log, day)*100:5.1f}% build pass rate")

    print("\n=== Tests Modified by Agent (skip/deleted) ===")
    agent_changes = log[log.modified_by == "agent"][["test_id", "test_name", "module", "status"]].drop_duplicates()
    for _, r in agent_changes.sort_values("test_id").iterrows():
        print(f"  {r.test_id}  {r.test_name:<32} [{r.module}]  -> {r.status}")
    print(f"  Total: {len(agent_changes)} tests silently disabled without a named human sign-off")

    print("\n=== Cross-Reference with Incident Record ===")
    for _, inc in incident.iterrows():
        caught_by = inc["would_have_been_caught_by"]
        match = agent_changes[agent_changes.test_name == caught_by]
        if not match.empty:
            print(f"  Day {inc['day']}: {inc['event']} in '{inc['affected_module']}'")
            print(f"    -> would have been caught by: {caught_by}")
            print(f"    -> that test was disabled on Day {inc['test_disabled_on_day']} (status: {inc['test_status_at_time']})")
            print(f"    -> engineering hours spent on incident response: {inc['engineering_hours_incident_response']}")
            print(f"    CONFIRMED: disabled test and production incident are the same test.")

if __name__ == "__main__":
    main()
