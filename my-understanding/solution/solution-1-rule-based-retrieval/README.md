# Knowledge Items: Extraction + Retrieval Testing

This folder contains a working proof-of-concept for extracting provisioning domain
knowledge from prompt files and testing retrieval accuracy.

## What's Here

```
knowledge-items/
├── README.md                     # This file
├── retrieval_eval.py             # Retrieval logic + evaluation runner
├── test_scenarios.yaml           # 7 test scenarios with expected results
├── eval_results.json             # Output from last eval run
└── provisioning/                 # Extracted knowledge items
    ├── scope_rules.yaml          # 3 scope/gating rules
    ├── state_definitions.yaml    # 10 state definitions (service, resource, operational)
    ├── decision_trees.yaml       # 6 decision trees (including master flow)
    ├── tool_contracts.yaml       # 3 tool contracts (MCP tool mappings)
    └── evidence_and_failures.yaml # 3 evidence patterns + 2 failure patterns
```

## Current Coverage

27 knowledge items extracted from `ProvisioningManagerInvestigator_Instruction.md`,
covering 5 complete diagnostic paths:

- DT#1: No resource (cpeId null)
- DT#2: Resource assigned, device never online
- DT#3: Happy path (everything working)
- DT#7: Service locked by another process
- DT#8: ACS succeeded but PPPOE_RESET missing

Plus scope gating (out-of-scope and missing serviceId).

## How to Run

```bash
pip install pyyaml
python retrieval_eval.py
```

No LLM, no database, no external services needed.

## How to Iterate

### Add more knowledge items

1. Read a section of the prompt file
2. Create a YAML item following the schema in existing files
3. Add `related_to` edges to connect it to other items
4. Add the new item's knowledge_id to relevant test scenario `expected_retrieved`

### Add more test scenarios

1. Think of a user problem
2. Define mock tool responses (what state would the tools return?)
3. Determine which decision tree should match
4. List expected items (decision tree + states + tools + evidence + failures)
5. List items that should NOT be retrieved
6. Add to `test_scenarios.yaml`

### Improve retrieval logic

The current retrieval in `retrieval_eval.py` is rule-based (mirrors the master
diagnostic flow from the prompt). To test a different retrieval strategy:

1. Write a new retrieval function with the same signature as `retrieve_by_rules`
2. Swap it into `evaluate_scenario`
3. Run the eval and compare scores

Potential strategies to test:
- Semantic search (embed user_input, find closest decision trees by statement)
- Hybrid (hard filter + semantic ranking)
- Graph traversal (match state combination, walk edges)

### When to move to a real backend

Move when:
- You have 50+ items and YAML files become unwieldy
- You need semantic search (user input doesn't map cleanly to preconditions)
- You need to test with actual LLM agents (not just rule-based retrieval)
- You need to test multi-domain retrieval (provisioning + wifi + other)

The YAML items and test scenarios transfer directly to any backend.

## What's NOT Covered Yet

From the full prompt file (~100 items total), these are not yet extracted:

- Decision trees 4, 5, 6, 9, 10, 11, 12, 13
- Transition rules (service state transitions, resource state transitions)
- Workflow steps (pre-provisioning flow, post-provisioning flow)
- Reference maps (diagnostic table, timing reference, TR-181 params)
- Management system determination logic
- Retry mechanism rules
- Migration diagnostics
- Feature flag impact rules

## Schema Reference

Each knowledge item has these fields:

| Field | Required | Description |
|---|---|---|
| knowledge_id | Yes | Unique identifier (format: `<type>_<short_name>_v<version>`) |
| domain | Yes | Business domain (e.g., `provisioning`) |
| knowledge_type | Yes | One of: scope_rule, state_definition, transition_rule, decision_tree, failure_pattern, evidence_pattern, tool_contract, workflow_step, reference_map |
| title | Yes | Human-readable title |
| statement | Yes | The actual knowledge content |
| preconditions | Yes | Conditions that must be true for this item to be relevant |
| expected_outcome | Yes | What should happen when this item is applied |
| source_file | Yes | Where this was extracted from |
| source_section | Yes | Specific section in the source |
| source_kind | Yes | How it was extracted (prompt_extraction, code, chat, incident) |
| tenant_scope | Yes | Which tenants this applies to |
| environment_scope | Yes | Which environments (production, staging, etc.) |
| version | Yes | Item version |
| confidence | Yes | Confidence in correctness (0.0 - 1.0) |
| status | Yes | Lifecycle status: active, candidate, deprecated |
| tags | Yes | Searchable tags |
| related_to | No | Graph edges to other knowledge items |
