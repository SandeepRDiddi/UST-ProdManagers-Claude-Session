import numpy as np, pandas as pd

rng = np.random.default_rng(2026)

N_TASKS = 50
PHASES = ["Spec", "Plan", "Implement", "Test", "Review", "Debug"]

# Base token counts per phase at complexity=1, before scaling.
# Review is deliberately the highest base -- reflecting the real, cited 2026 finding
# that Review/iteration dominates total spend, not the initial Implement phase.
BASE_TOKENS = {
    "Spec": 800, "Plan": 1000, "Implement": 2000,
    "Test": 1200, "Review": 2500, "Debug": 1500,
}

# Illustrative token pricing ($ per million tokens). NOT current live pricing --
# state this explicitly in the demo. Output tokens priced ~5x input, within the
# real, cited 4-6x range.
PRICING = {
    "frontier": {"input": 3.00, "output": 15.00},
    "efficient": {"input": 0.25, "output": 1.25},
}

rows = []
task_id = 1
for _ in range(N_TASKS):
    complexity = int(rng.integers(1, 6))  # 1-5
    # Cubic scaling up to complexity=3 (matches the real, cited "3x complexity ->
    # ~27x token spend" 2026 finding exactly: 1^3=1, 3^3=27), then dampened growth
    # beyond that so complexity=5 doesn't become absurd in absolute terms.
    if complexity <= 3:
        complexity_multiplier = complexity ** 3
    else:
        complexity_multiplier = 27 * (1 + (complexity - 3) * 1.3)

    for phase in PHASES:
        base = BASE_TOKENS[phase]
        noise = rng.uniform(0.85, 1.15)
        tokens = base * complexity_multiplier * noise
        tokens = max(200, tokens)

        # Review phase gets extra inflation from iteration loops -- independent of complexity,
        # this is the real mechanism (retries, re-explaining context) the 2026 studies point to.
        iteration_loops = 0
        if phase == "Review":
            iteration_loops = int(rng.integers(0, 4))
            tokens *= (1 + iteration_loops * 0.45)
        elif phase == "Debug":
            iteration_loops = int(rng.integers(0, 3))
            tokens *= (1 + iteration_loops * 0.35)

        tokens = int(tokens)
        input_tokens = int(tokens * 0.70)
        output_tokens = tokens - input_tokens

        # Model routing: Implement/Test/Debug/Review always use the frontier model (precision-critical).
        # Spec/Plan are lower-stakes and CAN use an efficient model -- but in this simulated org,
        # only 35% of eligible low-complexity Spec/Plan tasks actually do. The rest are the
        # hybrid-routing waste CostGuard exists to catch.
        if phase in ("Spec", "Plan") and complexity <= 2 and rng.random() < 0.35:
            model = "efficient"
        else:
            model = "frontier"

        cost = (input_tokens / 1_000_000 * PRICING[model]["input"] +
                output_tokens / 1_000_000 * PRICING[model]["output"])

        rows.append({
            "task_id": f"T-{task_id:03d}", "complexity": complexity, "phase": phase,
            "model": model, "iteration_loops": iteration_loops,
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens, "cost_usd": round(cost, 4),
        })
    task_id += 1

df = pd.DataFrame(rows)
df.to_csv("/mnt/user-data/outputs/sdlc_token_log.csv", index=False)

# ---- verification ----
print(f"Total tasks: {N_TASKS}, total phase-records: {len(df)}")
print(f"\nTotal cost across all tasks: ${df.cost_usd.sum():,.2f}")

by_phase = df.groupby("phase").agg(total_cost=("cost_usd", "sum"), total_tokens=("total_tokens", "sum")).sort_values("total_cost", ascending=False)
by_phase["pct_of_total"] = (by_phase.total_cost / df.cost_usd.sum() * 100).round(1)
print("\nCost by SDLC phase:")
print(by_phase.to_string())

# complexity scaling check
c1 = df[(df.complexity == 1) & (df.phase == "Implement")].total_tokens.mean()
c3 = df[(df.complexity == 3) & (df.phase == "Implement")].total_tokens.mean()
print(f"\nComplexity scaling check (Implement phase): complexity=1 avg={c1:.0f} tokens, "
      f"complexity=3 avg={c3:.0f} tokens, ratio={c3/c1:.1f}x")

# hybrid-routing waste check
waste = df[(df.phase.isin(["Spec","Plan"])) & (df.complexity <= 2) & (df.model == "frontier")]
if len(waste) > 0:
    hypothetical_efficient_cost = (waste.input_tokens/1_000_000*PRICING["efficient"]["input"] +
                                    waste.output_tokens/1_000_000*PRICING["efficient"]["output"]).sum()
    actual_cost = waste.cost_usd.sum()
    print(f"\nHybrid-routing waste: {len(waste)} low-complexity Spec/Plan tasks ran on the frontier model.")
    print(f"  Actual cost: ${actual_cost:,.2f}  |  Cost if routed to efficient model: ${hypothetical_efficient_cost:,.2f}")
    print(f"  Potential savings: ${actual_cost-hypothetical_efficient_cost:,.2f} ({(1-hypothetical_efficient_cost/actual_cost)*100:.0f}% reduction on these tasks)")
