#!/usr/bin/env python3
"""
drift_watcher.py -- a context-aware agent configured on a hypothesis.

The hypothesis: "The claims in context_claims.yaml are still true of the real
system." This agent tests that hypothesis against Rank 1-3 sources on the
Trust Hierarchy (source code, config) -- never against README.md itself,
which is the thing being checked, not a source of truth.

Run this in CI on every merge and it catches doc-vs-code drift the day it
happens, instead of three months later in a client conversation.

Usage:
    python3 drift_watcher.py [claims_file]   # defaults to context_claims.yaml
"""
import sys
import importlib
import yaml
from pathlib import Path


def load_yaml_path(file_path: str, dotted_path: str):
    with open(file_path) as f:
        data = yaml.safe_load(f)
    for key in dotted_path.split("."):
        data = data[key]
    return data


def load_python_attr(module_name: str, attr_name: str):
    module = importlib.import_module(module_name)
    return getattr(module, attr_name)


def values_match(check_type: str, doc_value, real_value) -> bool:
    if check_type == "set_equals":
        return set(doc_value) == set(real_value)
    if check_type == "equals":
        return doc_value == real_value
    raise ValueError(f"Unknown check type: {check_type}")


def run(claims_file: str):
    with open(claims_file) as f:
        claims = yaml.safe_load(f)["claims"]

    results = []
    for claim in claims:
        try:
            if claim["source_type"] == "python_attr":
                real_value = load_python_attr(claim["module"], claim["attr"])
            elif claim["source_type"] == "yaml_path":
                real_value = load_yaml_path(claim["file"], claim["path"])
            else:
                raise ValueError(f"Unknown source_type: {claim['source_type']}")

            match = values_match(claim["check"], claim["doc_claim"], real_value)
            results.append({
                "name": claim["name"], "description": claim["description"],
                "doc_claim": claim["doc_claim"], "real_value": real_value,
                "status": "MATCH" if match else "DRIFT",
            })
        except Exception as e:
            results.append({
                "name": claim["name"], "description": claim["description"],
                "doc_claim": claim["doc_claim"], "real_value": f"ERROR: {e}",
                "status": "ERROR",
            })
    return results


def main():
    claims_file = sys.argv[1] if len(sys.argv) > 1 else "context_claims.yaml"
    results = run(claims_file)

    drift_count = sum(1 for r in results if r["status"] == "DRIFT")
    print(f"Context-Aware Drift Check -- {len(results)} claims tested\n")
    for r in results:
        marker = {"MATCH": "OK   ", "DRIFT": "DRIFT", "ERROR": "ERR  "}[r["status"]]
        print(f"[{marker}] {r['name']}: doc says {r['doc_claim']!r}, real value is {r['real_value']!r}")

    print(f"\n{drift_count} of {len(results)} claims have drifted from documentation.")
    if drift_count > 0:
        print("Recommendation: do not repeat these documented values to a client without verifying "
              "against the values above first. File a doc-update ticket.")
        sys.exit(1)  # non-zero exit -- this is what makes it usable as a CI gate
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
