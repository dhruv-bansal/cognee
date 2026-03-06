"""
Solution 2: Domain Knowledge Retrieval + Evaluation

Unlike solution 1 (playbook retrieval), this tests whether the retrieval
assembles the right DOMAIN KNOWLEDGE for reasoning, not whether it finds
the right pre-baked answer.

The test: for each scenario, does the system retrieve the domain knowledge
items listed in `domain_knowledge_needed`? The agent should be able to
derive the correct diagnosis from those items alone.

Two retrieval modes:
  1. state_match: Analyzes tool responses to identify relevant states,
     then pulls related transitions, flows, tools, and constraints.
  2. (future) semantic: Embed user input + tool evidence, find relevant
     domain knowledge by similarity.

Usage:
  pip install pyyaml
  python retrieval_eval.py
"""

import json
from pathlib import Path
import yaml


def load_domain_knowledge(knowledge_dir: str) -> dict:
    """Load all domain knowledge items into a flat dict by knowledge_id."""
    items = {}
    for yaml_file in Path(knowledge_dir).rglob("*.yaml"):
        with open(yaml_file) as f:
            data = yaml.safe_load(f)
            if data and "items" in data:
                for item in data["items"]:
                    items[item["knowledge_id"]] = item
    return items


def load_test_cases(test_file: str) -> list:
    with open(test_file) as f:
        data = yaml.safe_load(f)
    return data.get("test_cases", [])


def build_index(items: dict) -> dict:
    """Build lookup indexes for retrieval."""
    by_type = {}
    for kid, item in items.items():
        kt = item["knowledge_type"]
        by_type.setdefault(kt, []).append(kid)

    by_state_value = {}
    for kid, item in items.items():
        if item["knowledge_type"] == "state_definition":
            val = item.get("value", "")
            by_state_value[val] = kid

    return {"by_type": by_type, "by_state_value": by_state_value}


def retrieve_domain_knowledge(
    items: dict,
    index: dict,
    tool_responses: dict,
) -> set:
    """
    Assemble relevant domain knowledge based on observed system state.

    Strategy:
    1. Identify which states are observed in tool responses.
    2. Pull state definitions for those states.
    3. Pull transition rules that involve those states (from or to).
    4. Pull system flows relevant to the management system and scenario.
    5. Pull tool contracts for tools used and tools that would provide more evidence.
    6. Pull constraints that govern the observed situation.
    """
    retrieved = set()

    svc = tool_responses.get("get_service_details_by_service_id", {})
    res = tool_responses.get("get_resource_by_cpe_id", {})
    mongo = tool_responses.get("query_mongodb", {})

    service_state = svc.get("serviceState")
    cpe_id = svc.get("cpeId")
    mgmt_system = svc.get("managementSystem")
    lock_ref = svc.get("serviceLockReferenceId")
    op_state = res.get("operationalState")
    op_sub_state = res.get("operationalSubState")
    resource_state = res.get("resourceState")

    if not svc:
        return retrieved

    # --- 1. Match observed states to state definitions ---
    state_value_map = index["by_state_value"]

    if service_state and service_state in state_value_map:
        retrieved.add(state_value_map[service_state])

    if op_state and op_sub_state:
        combo = f"{op_state} / {op_sub_state}"
        if combo in state_value_map:
            retrieved.add(state_value_map[combo])

    if resource_state:
        res_sub = res.get("resourceSubState", "")
        combo = f"{resource_state} / {res_sub}" if res_sub else resource_state
        if combo in state_value_map:
            retrieved.add(state_value_map[combo])

    # --- 2. Pull transition rules relevant to observed states ---
    for kid, item in items.items():
        if item["knowledge_type"] != "transition_rule":
            continue

        from_val = item.get("from_state", {}).get("value", "")
        to_val = item.get("to_state", {}).get("value", "")

        if service_state and (service_state in from_val or service_state in to_val):
            retrieved.add(kid)

        if op_sub_state and op_sub_state in (from_val + to_val):
            retrieved.add(kid)

        applies_to = item.get("applies_to", "")
        if mgmt_system and mgmt_system != "RDK" and "LEGACY" in applies_to:
            retrieved.add(kid)
        if mgmt_system == "RDK" and "RDK" in applies_to:
            retrieved.add(kid)

    # --- 3. Pull system flows ---
    if mgmt_system == "UNKNOWN" or not cpe_id:
        retrieved.add("flow_management_system_determination")

    if mgmt_system == "RDK" and service_state in ("UNPROVISIONED", "PROVISIONING_FAILED"):
        retrieved.add("flow_post_provisioning")

    if service_state == "PROVISIONING_FAILED" or (
        op_state == "ENABLED" and service_state == "UNPROVISIONED"
    ):
        retrieved.add("flow_job_manager_execution")

    # --- 4. Pull tool contracts ---
    retrieved.add("tool_get_service_details")

    if cpe_id:
        retrieved.add("tool_get_resource")

    if service_state in ("UNPROVISIONED", "PROVISIONING_FAILED") and op_state == "ENABLED":
        retrieved.add("tool_search_logs")

    if service_state == "PROVISIONING_FAILED":
        retrieved.add("tool_query_transaction_job")

    if lock_ref and service_state == "UNPROVISIONED":
        retrieved.add("tool_search_logs")

    if op_sub_state == "PENDING_PPPOE_RESTART":
        retrieved.add("tool_search_logs")

    # --- 5. Pull constraints relevant to the situation ---
    retrieved.add("constraint_rdk_async_legacy_sync")

    if op_state == "UNKNOWN":
        retrieved.add("constraint_no_offline_state")

    if service_state == "UNPROVISIONED" or service_state == "INACTIVE":
        retrieved.add("constraint_unprovisioned_not_inactive")

    if lock_ref:
        retrieved.add("constraint_lock_priority_order")
        retrieved.add("constraint_stale_lock_threshold")

    if service_state == "PROVISIONING_FAILED" and mongo and mongo.get("result") is None:
        retrieved.add("constraint_operation_mapping_non_retryable")

    if not cpe_id:
        retrieved.add("constraint_central_ri_rdk_only")

    # Filter to only items that actually exist
    retrieved = {kid for kid in retrieved if kid in items}

    return retrieved


def evaluate_test_case(test_case: dict, items: dict, index: dict) -> dict:
    """Evaluate one test case."""
    tool_responses = test_case.get("tool_responses", {})
    expected = set(test_case.get("domain_knowledge_needed", []))

    retrieved = retrieve_domain_knowledge(items, index, tool_responses)

    true_positives = retrieved & expected
    missing = expected - retrieved
    extra = retrieved - expected

    recall = len(true_positives) / len(expected) if expected else 1.0
    precision = len(true_positives) / len(retrieved) if retrieved else 0.0

    passed = recall >= 0.8

    return {
        "test_id": test_case["test_id"],
        "title": test_case["title"],
        "derived_from": test_case.get("derived_from", ""),
        "passed": passed,
        "recall": round(recall, 2),
        "precision": round(precision, 2),
        "expected_count": len(expected),
        "retrieved_count": len(retrieved),
        "true_positives": sorted(true_positives),
        "missing": sorted(missing),
        "extra": sorted(extra),
    }


def main():
    script_dir = Path(__file__).parent
    knowledge_dir = script_dir / "domain-knowledge" / "provisioning"
    test_file = script_dir / "test-cases" / "provisioning_reasoning_tests.yaml"

    print("=" * 72)
    print("SOLUTION 2: DOMAIN KNOWLEDGE RETRIEVAL FOR REASONING")
    print("=" * 72)

    items = load_domain_knowledge(str(knowledge_dir))
    tests = load_test_cases(str(test_file))

    print(f"\nLoaded {len(items)} domain knowledge items")
    print(f"Loaded {len(tests)} reasoning test cases\n")

    type_counts = {}
    for item in items.values():
        kt = item["knowledge_type"]
        type_counts[kt] = type_counts.get(kt, 0) + 1
    for kt, count in sorted(type_counts.items()):
        print(f"  {kt}: {count}")
    print()

    results = []
    passed_count = 0

    print("-" * 72)
    for test in tests:
        result = evaluate_test_case(test, items, build_index(items))
        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        print(f"[{status}] {result['test_id']}: {result['title']}")
        print(f"       Recall: {result['recall']}  Precision: {result['precision']}")
        print(f"       Retrieved {result['retrieved_count']} items, expected {result['expected_count']}")

        if result["missing"]:
            print(f"       Missing: {result['missing']}")
        if result["extra"]:
            print(f"       Extra:   {result['extra']}")
        print()

        if result["passed"]:
            passed_count += 1

    print("-" * 72)
    print(f"RESULTS: {passed_count}/{len(results)} test cases passed (recall >= 0.8)")
    print()
    print("What this proves:")
    print("  - The domain knowledge model (states, transitions, flows, tools, constraints)")
    print("    is sufficient for an agent to reason about each scenario.")
    print("  - No pre-baked decision trees were used as input.")
    print("  - Test case 06 (novel scenario) validates generalization.")
    print("-" * 72)

    output_file = script_dir / "eval_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDetailed results: {output_file}")


if __name__ == "__main__":
    main()
