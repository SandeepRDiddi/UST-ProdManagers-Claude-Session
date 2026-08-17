#!/usr/bin/env python3
"""
costguard.py -- governance-as-code for agentic SDLC token spend.

Philosophy (Session 10): govern the spend the same way Session 7 governed
autonomy -- explicit, versioned thresholds in a config file, not a runtime
judgment call. CostGuard doesn't stop agents from working. It flags the
three real 2026 failure patterns this session is built around:

  1. A phase blowing past its budget (visibility -- the thing 80% of
     companies lack, per the 2026 State of AI Cost Governance Report)
  2. Non-linear complexity spend -- a task costing far more than its
     stated complexity should predict
  3. Hybrid-routing waste -- a frontier model used on a task an efficient
     model could have handled

Usage:
    python3 costguard.py sdlc_token_log.csv budget_config.yaml
"""
import sys
import csv
import yaml
from collections import defaultdict

PRICING = {
    "frontier": {"input": 3.00, "output": 15.00},
    "efficient": {"input": 0.25, "output": 1.25},
}


def load_log(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["complexity"] = int(r["complexity"])
        r["input_tokens"] = int(r["input_tokens"])
        r["output_tokens"] = int(r["output_tokens"])
        r["total_tokens"] = int(r["total_tokens"])
        r["cost_usd"] = float(r["cost_usd"])
    return rows


def load_budget(path):
    with open(path) as f:
        return yaml.safe_load(f)


def check_phase_budgets(rows, budget):
    spend_by_phase = defaultdict(float)
    for r in rows:
        spend_by_phase[r["phase"]] += r["cost_usd"]

    print("GOVERN -- phase budget check (thresholds from budget_config.yaml, not ad hoc):")
    breaches = []
    for phase, cap in budget["phase_budget_usd"].items():
        actual = spend_by_phase.get(phase, 0)
        status = "OVER BUDGET" if actual > cap else "within budget"
        marker = "  [FLAG]" if actual > cap else ""
        print(f"  {phase:<12} ${actual:>8.2f} / ${cap:>8.2f} cap  -- {status}{marker}")
        if actual > cap:
            breaches.append((phase, actual, cap))
    return breaches


def check_complexity_outliers(rows, budget):
    print("\nMEASURE -- non-linear complexity outliers (task cost vs. its complexity rating):")
    by_task = defaultdict(lambda: {"complexity": None, "cost": 0.0})
    for r in rows:
        t = by_task[r["task_id"]]
        t["complexity"] = r["complexity"]
        t["cost"] += r["cost_usd"]

    threshold = budget["complexity_outlier_multiplier"]
    baseline = {}
    for c in range(1, 6):
        costs = [t["cost"] for t in by_task.values() if t["complexity"] == c]
        baseline[c] = sum(costs) / len(costs) if costs else 0

    flagged = []
    for task_id, t in by_task.items():
        expected = baseline[t["complexity"]]
        if expected > 0 and t["cost"] > expected * threshold:
            flagged.append((task_id, t["complexity"], t["cost"], expected))

    if flagged:
        for task_id, c, cost, expected in flagged:
            print(f"  [FLAG] {task_id} (complexity {c}): ${cost:.2f} vs. ${expected:.2f} average for that complexity")
    else:
        print("  No outliers beyond the configured multiplier.")
    return flagged


def check_hybrid_routing_waste(rows, budget):
    print("\nMANAGE -- hybrid-routing waste (frontier model used where efficient would do):")
    eligible = [r for r in rows if r["phase"] in budget["hybrid_eligible_phases"]
                and r["complexity"] <= budget["hybrid_eligible_max_complexity"]
                and r["model"] == "frontier"]
    if not eligible:
        print("  No hybrid-routing waste found.")
        return 0

    actual_cost = sum(r["cost_usd"] for r in eligible)
    hypothetical_cost = sum(
        r["input_tokens"]/1_000_000*PRICING["efficient"]["input"] +
        r["output_tokens"]/1_000_000*PRICING["efficient"]["output"]
        for r in eligible
    )
    savings = actual_cost - hypothetical_cost
    print(f"  {len(eligible)} task-phases eligible for routing to the efficient model, but didn't.")
    print(f"  Actual cost: ${actual_cost:.2f}  |  Cost if routed correctly: ${hypothetical_cost:.2f}")
    print(f"  Recoverable: ${savings:.2f} ({(1-hypothetical_cost/actual_cost)*100:.0f}% reduction on these task-phases)")
    return savings


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 costguard.py <sdlc_token_log.csv> <budget_config.yaml>")
        sys.exit(1)

    rows = load_log(sys.argv[1])
    budget = load_budget(sys.argv[2])

    total_cost = sum(r["cost_usd"] for r in rows)
    print(f"CostGuard -- {len(set(r['task_id'] for r in rows))} tasks, {len(rows)} phase-records, "
          f"${total_cost:.2f} total spend\n")

    breaches = check_phase_budgets(rows, budget)
    outliers = check_complexity_outliers(rows, budget)
    savings = check_hybrid_routing_waste(rows, budget)

    print(f"\nSUMMARY: {len(breaches)} phase(s) over budget, {len(outliers)} complexity outlier(s), "
          f"${savings:.2f} in recoverable hybrid-routing waste.")
    sys.exit(1 if (breaches or outliers) else 0)


if __name__ == "__main__":
    main()
