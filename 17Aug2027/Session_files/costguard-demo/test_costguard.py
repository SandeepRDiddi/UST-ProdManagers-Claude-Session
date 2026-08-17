"""
test_costguard.py -- proves CostGuard's budget check actually distinguishes
over-budget from within-budget, and correctly finds the hybrid-routing waste.
"""
import csv
import yaml
import costguard


def write_csv(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["task_id","complexity","phase","model",
                            "iteration_loops","input_tokens","output_tokens","total_tokens","cost_usd"])
        w.writeheader()
        w.writerows(rows)


def test_within_budget_raises_no_flag(tmp_path):
    # a single cheap task, nowhere near any phase cap
    rows = [{"task_id":"T-001","complexity":1,"phase":"Spec","model":"efficient",
             "iteration_loops":0,"input_tokens":500,"output_tokens":200,
             "total_tokens":700,"cost_usd":0.01}]
    csv_path = tmp_path / "log.csv"
    write_csv(csv_path, rows)
    budget = {"phase_budget_usd": {"Spec": 12.0}, "complexity_outlier_multiplier": 2.5,
              "hybrid_eligible_phases": ["Spec"], "hybrid_eligible_max_complexity": 2}
    loaded = costguard.load_log(csv_path)
    breaches = costguard.check_phase_budgets(loaded, budget)
    assert breaches == []


def test_over_budget_task_is_flagged(tmp_path):
    rows = [{"task_id":"T-002","complexity":5,"phase":"Review","model":"frontier",
             "iteration_loops":3,"input_tokens":900000,"output_tokens":400000,
             "total_tokens":1300000,"cost_usd":50.0}]
    csv_path = tmp_path / "log.csv"
    write_csv(csv_path, rows)
    budget = {"phase_budget_usd": {"Review": 35.0}, "complexity_outlier_multiplier": 2.5,
              "hybrid_eligible_phases": [], "hybrid_eligible_max_complexity": 2}
    loaded = costguard.load_log(csv_path)
    breaches = costguard.check_phase_budgets(loaded, budget)
    assert len(breaches) == 1
    assert breaches[0][0] == "Review"


def test_real_dataset_flags_exactly_review():
    loaded = costguard.load_log("sdlc_token_log.csv")
    budget = costguard.load_budget("budget_config.yaml")
    breaches = costguard.check_phase_budgets(loaded, budget)
    assert [b[0] for b in breaches] == ["Review"]


def test_real_dataset_finds_hybrid_waste():
    loaded = costguard.load_log("sdlc_token_log.csv")
    budget = costguard.load_budget("budget_config.yaml")
    savings = costguard.check_hybrid_routing_waste(loaded, budget)
    assert savings > 0
