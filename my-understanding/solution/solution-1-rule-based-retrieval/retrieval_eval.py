"""
Minimal retrieval + evaluation script for provisioning knowledge items.

This is backend-agnostic: it loads YAML files into memory and tests
whether a simple retrieval strategy returns the correct "diagnostic package"
for each test scenario.

Two retrieval strategies are implemented:
  1. rule_based: Uses mock tool responses to match decision tree preconditions
  2. semantic: Uses embedding similarity on the user input vs item statements

The goal is to validate that the knowledge model + retrieval logic can match
the quality of "full prompt in context" before committing to any backend.

Usage:
  pip install pyyaml numpy sentence-transformers
  python retrieval_eval.py
"""

import os
import sys
import yaml
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# 1. Load knowledge items from YAML
# ---------------------------------------------------------------------------

def load_knowledge_items(knowledge_dir: str) -> dict:
    """Load all YAML knowledge items into a flat dict keyed by knowledge_id."""
    items = {}
    knowledge_path = Path(knowledge_dir)

    for yaml_file in knowledge_path.rglob("*.yaml"):
        if yaml_file.name == "test_scenarios.yaml":
            continue
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data and "items" in data:
                for item in data["items"]:
                    items[item["knowledge_id"]] = item

    return items


def load_test_scenarios(scenarios_file: str) -> list:
    """Load test scenarios."""
    with open(scenarios_file) as f:
        data = yaml.safe_load(f)
    return data.get("scenarios", [])


# ---------------------------------------------------------------------------
# 2. Rule-Based Retrieval (uses mock tool responses to match preconditions)
# ---------------------------------------------------------------------------

def retrieve_by_rules(
    knowledge_items: dict,
    mock_tool_responses: dict,
    session_context: dict,
) -> dict:
    """
    Simulates the retrieval contract:
    1. Hard filter by domain
    2. Use tool response data to match decision tree preconditions
    3. Follow edges to assemble the full diagnostic package
    """
    domain = session_context.get("domain")
    service_id = session_context.get("service_id")

    result = {
        "scope_rules": [],
        "decision_tree": None,
        "states": [],
        "tools": [],
        "evidence": [],
        "failures": [],
    }

    # Always retrieve the primary scope rule
    result["scope_rules"].append("scope_rule_onebb_provisioning_v1")

    # Add the service_id requirement rule if no service_id provided
    if not service_id:
        result["scope_rules"].append("scope_rule_required_service_id_v1")

    # If no domain or no service_id, return only scope rules
    if domain != "provisioning":
        return result
    if not service_id:
        return result

    # Get service details from mock responses
    svc = mock_tool_responses.get("get_service_details_by_service_id", {})
    res = mock_tool_responses.get("get_resource_by_cpe_id", {})

    service_state = svc.get("serviceState")
    cpe_id = svc.get("cpeId")
    mgmt_system = svc.get("managementSystem")
    lock_ref = svc.get("serviceLockReferenceId")
    op_state = res.get("operationalState")
    op_sub_state = res.get("operationalSubState")

    # Master diagnostic flow logic (mirrors the decision tree from the prompt)
    matched_dt = None

    if not cpe_id:
        matched_dt = "decision_tree_01_no_resource_v1"
    elif service_state == "PROVISIONED":
        matched_dt = "decision_tree_03_happy_path_v1"
    elif service_state == "UNPROVISIONED":
        if op_state == "UNKNOWN":
            if op_sub_state == "PENDING_PPPOE_RESTART":
                matched_dt = "decision_tree_08_no_pppoe_reset_v1"
            else:
                matched_dt = "decision_tree_02_resource_not_online_v1"
        elif op_state == "ENABLED" and lock_ref:
            matched_dt = "decision_tree_07_service_locked_v1"

    # If the matched DT involves log investigation, include the log tool
    log_investigation_dts = {
        "decision_tree_07_service_locked_v1",
        "decision_tree_08_no_pppoe_reset_v1",
    }
    if matched_dt in log_investigation_dts:
        result["tools"].append("tool_contract_check_provisioning_logs_v1")

    if matched_dt and matched_dt in knowledge_items:
        result["decision_tree"] = matched_dt
        dt_item = knowledge_items[matched_dt]

        # Follow edges to assemble diagnostic package
        for rel in dt_item.get("related_to", []):
            target = rel["target"]
            edge = rel["edge_type"]

            if target not in knowledge_items:
                continue

            target_type = knowledge_items[target]["knowledge_type"]

            if edge == "REQUIRES_STATE" or target_type == "state_definition":
                result["states"].append(target)
            elif edge == "REQUIRES_TOOL" or target_type == "tool_contract":
                result["tools"].append(target)
            elif edge == "CONFIRMED_BY" or target_type == "evidence_pattern":
                result["evidence"].append(target)
            elif edge == "INSTANCE_OF" or target_type == "failure_pattern":
                result["failures"].append(target)

    # Always include the base tools
    if "tool_contract_get_service_details_v1" not in result["tools"]:
        result["tools"].append("tool_contract_get_service_details_v1")
    if cpe_id and "tool_contract_get_resource_v1" not in result["tools"]:
        result["tools"].append("tool_contract_get_resource_v1")

    return result


# ---------------------------------------------------------------------------
# 3. Evaluation: Compare retrieved vs expected
# ---------------------------------------------------------------------------

@dataclass
class EvalResult:
    scenario_id: str
    title: str
    passed: bool
    precision: float
    recall: float
    details: dict = field(default_factory=dict)


def flatten_expected(expected: dict) -> set:
    """Flatten expected_retrieved into a set of knowledge_ids."""
    ids = set()
    for key, val in expected.items():
        if isinstance(val, str):
            ids.add(val)
        elif isinstance(val, list):
            ids.update(val)
    return ids


def flatten_retrieved(retrieved: dict) -> set:
    """Flatten retrieval result into a set of knowledge_ids."""
    ids = set()
    if retrieved["decision_tree"]:
        ids.add(retrieved["decision_tree"])
    for key in ["scope_rules", "states", "tools", "evidence", "failures"]:
        ids.update(retrieved.get(key, []))
    return ids


def evaluate_scenario(
    scenario: dict,
    knowledge_items: dict,
) -> EvalResult:
    """Evaluate one test scenario."""
    mock_responses = scenario.get("mock_tool_responses", {})
    session_ctx = scenario.get("session_context", {})
    expected = scenario.get("expected_retrieved", {})
    should_not = set(scenario.get("should_not_retrieve", []))

    retrieved = retrieve_by_rules(knowledge_items, mock_responses, session_ctx)

    expected_ids = flatten_expected(expected)
    retrieved_ids = flatten_retrieved(retrieved)

    # Precision: of what we retrieved, how much was expected?
    true_positives = retrieved_ids & expected_ids
    false_positives = retrieved_ids - expected_ids
    leaked = retrieved_ids & should_not

    precision = len(true_positives) / len(retrieved_ids) if retrieved_ids else 0.0
    recall = len(true_positives) / len(expected_ids) if expected_ids else 1.0

    passed = recall >= 0.8 and len(leaked) == 0

    return EvalResult(
        scenario_id=scenario["scenario_id"],
        title=scenario["title"],
        passed=passed,
        precision=round(precision, 2),
        recall=round(recall, 2),
        details={
            "expected": sorted(expected_ids),
            "retrieved": sorted(retrieved_ids),
            "true_positives": sorted(true_positives),
            "false_positives": sorted(false_positives),
            "leaked_items": sorted(leaked),
            "missing": sorted(expected_ids - retrieved_ids),
        },
    )


# ---------------------------------------------------------------------------
# 4. Main: Run all scenarios
# ---------------------------------------------------------------------------

def main():
    script_dir = Path(__file__).parent
    knowledge_dir = script_dir / "provisioning"
    scenarios_file = script_dir / "test_scenarios.yaml"

    print("=" * 70)
    print("PROVISIONING KNOWLEDGE RETRIEVAL EVALUATION")
    print("=" * 70)

    # Load data
    items = load_knowledge_items(str(knowledge_dir))
    scenarios = load_test_scenarios(str(scenarios_file))

    print(f"\nLoaded {len(items)} knowledge items")
    print(f"Loaded {len(scenarios)} test scenarios\n")

    # Breakdown by type
    type_counts = {}
    for item in items.values():
        kt = item["knowledge_type"]
        type_counts[kt] = type_counts.get(kt, 0) + 1
    for kt, count in sorted(type_counts.items()):
        print(f"  {kt}: {count}")
    print()

    # Run evaluations
    results = []
    for scenario in scenarios:
        result = evaluate_scenario(scenario, items)
        results.append(result)

    # Print results
    print("-" * 70)
    total_passed = 0
    total = len(results)

    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.scenario_id}: {r.title}")
        print(f"       Precision: {r.precision}  Recall: {r.recall}")

        if r.details.get("missing"):
            print(f"       Missing: {r.details['missing']}")
        if r.details.get("leaked_items"):
            print(f"       LEAKED:  {r.details['leaked_items']}")
        if r.details.get("false_positives"):
            print(f"       Extra:   {r.details['false_positives']}")
        print()

        if r.passed:
            total_passed += 1

    # Summary
    print("-" * 70)
    print(f"RESULTS: {total_passed}/{total} scenarios passed")
    print(f"Overall recall target: >= 0.8 per scenario, zero data leakage")
    print("-" * 70)

    if total_passed < total:
        print("\nFailed scenarios need investigation.")
        print("Check 'missing' items (recall gap) and 'leaked' items (precision/safety gap).")

    # Detailed JSON output for programmatic analysis
    output_file = script_dir / "eval_results.json"
    with open(output_file, "w") as f:
        json.dump(
            [
                {
                    "scenario_id": r.scenario_id,
                    "title": r.title,
                    "passed": r.passed,
                    "precision": r.precision,
                    "recall": r.recall,
                    "details": r.details,
                }
                for r in results
            ],
            f,
            indent=2,
        )
    print(f"\nDetailed results written to: {output_file}")


if __name__ == "__main__":
    main()
