# Solution 2: Domain Knowledge for Reasoning

## Core Idea

Domain agents should own **generic domain knowledge** about how their business domain
works, not pre-baked answers for specific use cases. The knowledge enables the agent
to reason about any problem, including novel ones never seen before.

See `agent.md > Core Architectural Principle` and `solution/00-approach-and-evolution.md`
for the full rationale.

## How This Differs From Solution 1

| Aspect | Solution 1 | Solution 2 |
|---|---|---|
| What is extracted | Decision trees (pre-baked answers) | How the system works (states, transitions, flows, tools, constraints) |
| What agent receives | "If X and Y, do Z" | "Here's how the system works" |
| What agent does | Follow the playbook | Reason about the problem |
| Novel problems | Fails (no matching playbook) | Reasons from first principles |
| Decision trees | Agent input | Test cases validating reasoning |

## What's Here

```
solution-2-domain-knowledge-reasoning/
├── README.md                        # This file
├── retrieval_eval.py                # Retrieval logic + eval runner
├── eval_results.json                # Last eval results
├── domain-knowledge/
│   └── provisioning/
│       ├── states.yaml              # 10 state definitions
│       ├── transitions.yaml         # 5 transition rules
│       ├── system_flows.yaml        # 4 system flow descriptions
│       ├── tools.yaml               # 4 tool contracts
│       └── constraints.yaml         # 8 invariants and constraints
└── test-cases/
    └── provisioning_reasoning_tests.yaml  # 7 reasoning test cases
```

## Knowledge Types (For Reasoning, Not Playbooks)

| Type | Count | What it captures | Why the agent needs it |
|---|---|---|---|
| `state_definition` | 10 | What states exist and their meaning | To understand observed system state |
| `transition_rule` | 5 | How states connect, what triggers changes | To reason about what should have happened |
| `system_flow` | 4 | How components interact end-to-end | To trace the path of an operation |
| `tool_contract` | 4 | What tools exist, what they return | To know how to gather evidence |
| `constraint` | 8 | Rules that are always true | To avoid incorrect reasoning |
| **Total** | **31** | | |

## Test Cases (Decision Trees Became Tests)

Each test case defines:
- A user problem
- Mock tool responses (what the system looks like)
- Which domain knowledge items the agent NEEDS to reason correctly
- Expected reasoning (how the agent should think)
- Expected conclusion (what the agent should decide)

**Test case 06 is the key one:** it tests a scenario from Decision Tree 11 (Operation
Mapping Not Found) but does NOT provide that decision tree. The agent must derive
the diagnosis from domain knowledge alone. This validates generalization.

## How to Run

```bash
pip install pyyaml
python retrieval_eval.py
```

Results: 7/7 pass, 100% recall (agent always gets the knowledge it needs).

Precision is intentionally looser than solution 1. Extra domain knowledge is acceptable
because it gives the agent MORE context to reason with. The critical metric is recall:
the agent must not miss knowledge it needs.

## How This Works at Production Scale

The retrieval in `retrieval_eval.py` is a simulation. In production, retrieval is
NOT pre-computed. The knowledge store is exposed as a **tool the agent queries
during reasoning** -- just like MCP tools for live state.

```
Agent reasoning loop:
  1. Query knowledge store: "What tools exist for provisioning diagnostics?"
  2. Call MCP tools to get live system state
  3. Query knowledge store: "What does PENDING_PPPOE_RESTART mean?"
  4. Query knowledge store: "What transitions apply from UNPROVISIONED?"
  5. Reason with accumulated knowledge + evidence → Diagnosis
```

Each query is scoped (by domain, by type, by keywords) and returns a small focused
set. This scales to 50+ domains because the agent only pulls what it needs for the
current reasoning step.

**Required store capabilities:**
- Metadata filtering: `domain=provisioning, type=constraint`
- Semantic search: `query="device not coming online"`
- Structured field match: `entity=service, value=UNPROVISIONED`

See `solution/00-approach-and-evolution.md` for full details.

## Next Steps

### 1. Load knowledge into a real store with search capabilities

Pick one: Postgres+pgvector, Cognee, or Qdrant. Load the 31 items. Implement
`search_knowledge` as an API the agent can call with filters + query text.

### 2. Build an end-to-end LLM reasoning test

Give an LLM these tools: `search_knowledge` + `get_service_details` (mocked) +
`get_resource` (mocked). Present a problem. Assert:
- Agent queries knowledge store
- Agent retrieves relevant items
- Agent reaches correct diagnosis

This is the real proof point for the architecture.

### 3. Extract remaining domain knowledge

Current coverage: ~31 of ~100 items. Remaining:
- More state definitions (draft sub-states, registration states, resource types)
- More transitions (resource transitions, operational state cycles)
- Retry mechanism rules (as constraints)
- Log patterns (enrichment to tool contracts)
- Migration flows, feature flag impacts

### 4. Add a second domain (WiFi Mesh)

Tests cross-domain isolation and whether the model generalizes.
