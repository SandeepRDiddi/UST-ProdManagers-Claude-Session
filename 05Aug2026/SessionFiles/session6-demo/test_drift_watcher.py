"""
test_drift_watcher.py -- proves drift_watcher correctly reports MATCH when a
claim is true, not just DRIFT when it's false. Run from the session4-demo/ root.
"""
import yaml
import drift_watcher


def test_true_claim_reports_match(tmp_path):
    claims_file = tmp_path / "claims.yaml"
    claims_file.write_text(yaml.dump({
        "claims": [{
            "name": "max_retries_correct",
            "description": "a claim that IS true, to prove MATCH works",
            "doc_claim": 2,  # the real value
            "source_type": "python_attr",
            "module": "src.notification_service",
            "attr": "MAX_RETRIES",
            "check": "equals",
        }]
    }))
    results = drift_watcher.run(str(claims_file))
    assert results[0]["status"] == "MATCH"


def test_false_claim_reports_drift(tmp_path):
    claims_file = tmp_path / "claims.yaml"
    claims_file.write_text(yaml.dump({
        "claims": [{
            "name": "max_retries_wrong",
            "description": "a claim that is FALSE, to prove DRIFT works",
            "doc_claim": 3,
            "source_type": "python_attr",
            "module": "src.notification_service",
            "attr": "MAX_RETRIES",
            "check": "equals",
        }]
    }))
    results = drift_watcher.run(str(claims_file))
    assert results[0]["status"] == "DRIFT"


def test_real_claims_file_finds_exactly_three_drifts():
    results = drift_watcher.run("context_claims.yaml")
    assert len(results) == 3
    assert all(r["status"] == "DRIFT" for r in results)
