# 04 - Knowledge Extraction Inventory & Data Shape Analysis

This document is a concrete analysis of `ProvisioningManagerInvestigator_Instruction.md`.
It inventories every discrete knowledge item, shows sample extractions, maps the
graph relationships between items, and assesses what storage backend actually fits.

---

## 1. Inventory: What Is Actually In This File

### Item Count by Knowledge Type

| Knowledge Type | Count | Examples |
|---|---|---|
| `scope_rule` | 4 | In-scope definition, out-of-scope examples, required identifier, cannot-determine response |
| `state_definition` | ~35 | 7 service states, 3 service statuses, 4 resource states + 5 draft sub-states, 6 operational state combos, 3 registration states, 3 resource types, 3 provisioning types, 3 lock types, 2 home states, 3 migration states |
| `transition_rule` | ~12 | 6 service transitions, 2 resource transitions (harmonized), 2 resource transitions (legacy), 2 operational state transitions |
| `decision_tree` | 13 | Decision Trees 1-12 + the master diagnostic flow (Key Diagnostic Questions) |
| `failure_pattern` | ~8 | ACS 520 error, operation mapping not found, partial success, stale lock, PPPOE_RESET missing, code error (NPE), certificate failure, retry exhaustion |
| `evidence_pattern` | ~10 | Successful provisioning log sequence, lock issue logs, ACS failure logs, Job Manager logs, event issue logs, at-a-glance fields, TransactionJob fields, ACS error codes |
| `tool_contract` | ~6 | Service Inventory lookup, Resource Inventory lookup, Job Manager/ACS request, Xmidt device communication, MongoDB TransactionJob query, Natco RI lookup |
| `workflow_step` | ~6 | Pre-provisioning flow (6 sub-steps), post-provisioning flow (6 sub-steps), PPPoE reset event flow, management system determination, pre-provisioning without resource |
| `reference_map` | ~8 | Management system outcome table, initial state by mgmt system, primary diagnostic table (13 scenarios), timing reference, microservices responsibility, TR-181 parameter mappings, retry config, feature flags |

**Total: ~100 discrete knowledge items in one prompt file.**

### What Stays in the Prompt (Not Extracted)

These sections are behavioral/persona instructions, not domain knowledge:

- "You are an advanced root cause analysis agent" (persona)
- "Use the following structure in your output" (output format)
- Tool usage rules ("you MUST cross-reference and use ONLY values explicitly defined") (safety)
- Confidence/unknowns instruction (behavioral)

---

## 2. Sample Extractions (Real Items From the File)

### Sample A: scope_rule

```yaml
knowledge_id: scope_rule_onebb_provisioning_v1
domain: provisioning
knowledge_type: scope_rule
title: "OneBroadband Provisioning Scope Definition"
statement: >
  This agent ONLY handles OneBroadband provisioning diagnostics: provisioning state,
  locks, CPEProvisioningEvent, ACS/Job Manager execution, PPPOE_RESET_EVENT,
  resource inventory/linking, online/offline operational state, operation mapping issues.
preconditions: []
expected_outcome: "Agent correctly identifies in-scope vs out-of-scope requests."
source_file: ProvisioningManagerInvestigator_Instruction.md
source_section: "Domain & Input Gating (MANDATORY)"
source_kind: prompt_extraction
tenant_scope: [all]
environment_scope: [production, staging]
version: "1.0"
confidence: 1.0
status: active
tags: [scope, gating, provisioning]
```

### Sample B: state_definition

```yaml
knowledge_id: state_def_service_unprovisioned_v1
domain: provisioning
knowledge_type: state_definition
title: "Service State: UNPROVISIONED"
statement: >
  Service not yet provisioned. Pre-provisioning complete, waiting for post-provisioning.
  This is the most common state for failed or incomplete provisioning.
  When provisioning fails or is incomplete, the service typically remains UNPROVISIONED,
  NOT INACTIVE. There is no persisted PROVISIONING state; flows move directly from
  UNPROVISIONED to either PROVISIONED or PROVISIONING_FAILED.
preconditions:
  - "Pre-provisioning has completed"
expected_outcome: "Agent understands UNPROVISIONED means waiting, not deactivated."
source_file: ProvisioningManagerInvestigator_Instruction.md
source_section: "Core Entities and States > Service Detail States"
source_kind: prompt_extraction
tenant_scope: [all]
environment_scope: [production, staging]
version: "1.0"
confidence: 1.0
status: active
tags: [state, service, unprovisioned]

# --- relationships (graph edges) ---
related_to:
  - target: state_def_service_provisioned_v1
    edge_type: TRANSITIONS_TO
    condition: "Successful device config + PPPOE_RESET received"
  - target: state_def_service_provisioning_failed_v1
    edge_type: TRANSITIONS_TO
    condition: "Device config failure after retries exhausted, NOT in PENDING_CHANGE"
  - target: decision_tree_02_resource_not_online_v1
    edge_type: DIAGNOSED_BY
  - target: decision_tree_04_offline_during_provisioning_v1
    edge_type: DIAGNOSED_BY
```

### Sample C: decision_tree

```yaml
knowledge_id: decision_tree_08_no_pppoe_reset_v1
domain: provisioning
knowledge_type: decision_tree
title: "Decision Tree 8: Params Applied (200 OK), No PPPOE_RESET Event"
statement: >
  ACS successfully applied parameters to CPE (200 OK received), but PPPOE_RESET
  event never arrived. Service remains UNPROVISIONED and LOCKED. Resource
  operationalSubState is PENDING_PPPOE_RESTART.
  PPPOE_RESET should arrive ~5 seconds after 200 OK from CPE.
preconditions:
  - "managementSystem == RDK"
  - "serviceState == UNPROVISIONED"
  - "resourceOperationalState == UNKNOWN"
  - "resourceOperationalSubState == PENDING_PPPOE_RESTART"
  - "serviceLockReferenceId is present"
  - "ACS response was 200 OK"
expected_outcome: >
  Investigate device-side PPPoE restart behavior. May need manual reprovisioning.
  Check event infrastructure (MQ) for issues. Device may need manual restart.
source_file: ProvisioningManagerInvestigator_Instruction.md
source_section: "Diagnostic Decision Trees > Decision Tree 8"
source_kind: prompt_extraction
tenant_scope: [all]
environment_scope: [production, staging]
version: "1.0"
confidence: 0.95
status: active
tags: [decision_tree, pppoe, reset, stuck, locked]

# --- relationships (graph edges) ---
related_to:
  - target: state_def_service_unprovisioned_v1
    edge_type: REQUIRES_STATE
  - target: state_def_resource_op_pending_pppoe_restart_v1
    edge_type: REQUIRES_STATE
  - target: tool_contract_check_asc_response_logs_v1
    edge_type: REQUIRES_TOOL
  - target: tool_contract_check_pppoe_event_logs_v1
    edge_type: REQUIRES_TOOL
  - target: evidence_pattern_pppoe_not_received_v1
    edge_type: CONFIRMED_BY
  - target: failure_pattern_pppoe_missing_v1
    edge_type: INSTANCE_OF
  - target: workflow_step_post_provisioning_pppoe_wait_v1
    edge_type: OCCURS_DURING
```

### Sample D: tool_contract

```yaml
knowledge_id: tool_contract_mongodb_transaction_job_v1
domain: provisioning
knowledge_type: tool_contract
title: "MongoDB TransactionJob Query"
statement: >
  Query the TransactionJob document in MongoDB 'transactions' collection to get
  execution results. Use transactionId (format: <id>_oneBroadband, with retry
  suffix for retries like _retry_1, _retry_2) as the primary correlation key.
  Key fields: transactionJobStatus (SUCCESS/PARTIAL_SUCCESS/FAILED),
  acsResponse.provisioningDetails (per-parameter results), manufacturer,
  productClass, softwareVersion.
preconditions:
  - "intent == verify_provisioning_execution OR intent == diagnose_acs_failure"
expected_outcome: >
  TransactionJob document showing execution status and per-parameter results.
  If no TransactionJob exists, indicates Operation Mapping failure (pre-execution).
source_file: ProvisioningManagerInvestigator_Instruction.md
source_section: "Job Manager Execution Details > TransactionJob Document"
source_kind: prompt_extraction
tenant_scope: [all]
environment_scope: [production, staging]
version: "1.0"
confidence: 1.0
status: active
tags: [tool, mongodb, transaction, job_manager]
mcp_tool_name: "query_mongodb_transactions"
mcp_tool_params:
  collection: transactions
  query_pattern: '{"transactionId": /.*_oneBroadband/}'

# --- relationships (graph edges) ---
related_to:
  - target: decision_tree_05_acs_error_v1
    edge_type: USED_BY
  - target: decision_tree_11_operation_mapping_v1
    edge_type: USED_BY
  - target: decision_tree_12_partial_success_v1
    edge_type: USED_BY
  - target: reference_map_job_manager_fields_v1
    edge_type: DOCUMENTS
```

### Sample E: failure_pattern

```yaml
knowledge_id: failure_pattern_operation_mapping_not_found_v1
domain: provisioning
knowledge_type: failure_pattern
title: "Operation Mapping Not Found (Job Manager)"
statement: >
  Job Manager cannot find the Operation Mapping for the device CPE specification.
  Lookup uses: Operation (setProvisioningParams) + Management System (RDK) +
  Manufacturer + Product Class + Software Version. This is NON-RETRYABLE.
  No TransactionJob is created. Service transitions to PROVISIONING_FAILED
  (unless in PENDING_CHANGE).
preconditions:
  - "managementSystem == RDK"
  - "device online (ENABLED/ONLINE)"
expected_outcome: >
  Update Operation Mapping Repository or correct device CPE specification.
log_signatures:
  - "cpe operation mapping not found for operation {} and cpeSpecification {}"
  - "product class or manufacturer missing for cpe specification {}"
  - "OperationNotSupportedException"
source_file: ProvisioningManagerInvestigator_Instruction.md
source_section: "Job Manager Execution Details > Operation Mapping Failures"
source_kind: prompt_extraction
tenant_scope: [all]
environment_scope: [production, staging]
version: "1.0"
confidence: 1.0
status: active
tags: [failure, operation_mapping, job_manager, non_retryable]

# --- relationships (graph edges) ---
related_to:
  - target: decision_tree_11_operation_mapping_v1
    edge_type: DIAGNOSED_BY
  - target: tool_contract_mongodb_transaction_job_v1
    edge_type: ABSENCE_CONFIRMS
    note: "No TransactionJob exists = confirms this failure pattern"
  - target: state_def_service_provisioning_failed_v1
    edge_type: CAUSES_STATE
  - target: reference_map_tr181_params_v1
    edge_type: RELATED_TO
```

---

## 3. The Relationship Graph (Why This Is Not a Flat Document Problem)

The items above are not independent. They form a dense graph:

```
                    ┌─────────────────┐
                    │   scope_rule    │
                    │ (in-scope def)  │
                    └────────┬────────┘
                             │ GATES
                             ▼
                    ┌─────────────────┐
            ┌──────│  decision_tree   │──────┐
            │      │ (DT #8: no PPPoE)│      │
            │      └────────┬────────┘      │
            │               │               │
    REQUIRES_STATE    REQUIRES_TOOL    CONFIRMED_BY
            │               │               │
            ▼               ▼               ▼
   ┌────────────────┐ ┌───────────┐ ┌───────────────┐
   │state_definition│ │tool_contract│ │evidence_pattern│
   │(UNPROVISIONED) │ │(check logs)│ │(log signatures)│
   └───────┬────────┘ └─────┬─────┘ └───────────────┘
           │                │
     TRANSITIONS_TO    USED_BY (other DTs)
           │                │
           ▼                ▼
   ┌────────────────┐ ┌────────────────┐
   │state_definition│ │ decision_tree  │
   │ (PROVISIONED)  │ │(DT #5: ACS err)│
   └────────────────┘ └────────────────┘
```

### Edge Types Needed (V1)

| Edge Type | Meaning | Example |
|---|---|---|
| `TRANSITIONS_TO` | State A can become State B under condition | UNPROVISIONED → PROVISIONED |
| `REQUIRES_STATE` | Decision tree expects this state combination | DT #8 requires UNPROVISIONED + PENDING_PPPOE_RESTART |
| `REQUIRES_TOOL` | Decision tree needs this tool for diagnosis | DT #8 needs log check + event check |
| `CONFIRMED_BY` | Evidence pattern confirms/rejects a hypothesis | "PPPOE_RESET_EVENT not received" log confirms DT #8 |
| `DIAGNOSED_BY` | A state/failure is diagnosed by this decision tree | UNPROVISIONED is diagnosed by DTs #1,2,4,5,6,7,8 |
| `INSTANCE_OF` | This decision tree scenario is an instance of a broader failure pattern | DT #8 is instance of "PPPOE missing" failure |
| `CAUSES_STATE` | This failure pattern leads to this state | Operation mapping failure → PROVISIONING_FAILED |
| `USED_BY` | This tool/reference is used by multiple decision trees | MongoDB query used by DTs #5, #11, #12 |
| `OCCURS_DURING` | This failure/scenario happens during this workflow step | DT #8 occurs during post-provisioning PPPoE wait |
| `DIFFERENTIATES_FROM` | This item helps distinguish between similar scenarios | Service lock (DT #7) vs ACS error (DT #6) |

### Estimated Graph Size

- **Nodes**: ~100 knowledge items
- **Edges**: ~250-350 relationships (each decision tree connects to 4-8 other items)
- **Dense hub nodes**: The 13-row diagnostic table and the master diagnostic flow connect to almost everything

---

## 4. What Storage Backend Fits This Data Shape

### What the retrieval actually needs to do

Given a user problem like "Customer 123's service is stuck in UNPROVISIONED, device is online":

1. **Hard filter**: domain=provisioning, tenant=X, environment=production, status=active
2. **Semantic match**: find decision trees whose `statement` or `preconditions` match "UNPROVISIONED + device online"
3. **Graph traversal**: from matched decision tree, follow REQUIRES_TOOL edges to get tool_contracts, follow CONFIRMED_BY edges to get evidence_patterns
4. **Assemble context**: decision tree + its required tools + its evidence patterns = one coherent diagnostic package

Steps 1-2 are standard filtered vector search.
Step 3 is WHERE the graph matters. Without it, you retrieve the decision tree but NOT its required tools and evidence. The agent gets "what to diagnose" but not "how to verify it."

### Backend Assessment (Based on Actual Data Shape)

| Capability Needed | Postgres + pgvector | Cognee (custom DataPoints) | Neo4j | Plain vector DB |
|---|---|---|---|---|
| Store ~100 items with custom metadata | Yes (table columns) | Yes (DataPoint subclasses) | Yes (node properties) | Partial (metadata filtering varies) |
| Hard filter by domain/tenant/env/status | Yes (SQL WHERE) | Needs custom query logic | Yes (Cypher WHERE) | Partial |
| Semantic search on statement text | Yes (pgvector) | Yes (built-in) | Yes (with vector index) | Yes |
| Graph traversal (DT → tools → evidence) | No (need JOINs, gets ugly) | Yes (graph engine underneath) | Yes (native) | No |
| Retrieve a "diagnostic package" (node + neighbors) | Hard (multiple JOINs) | Possible (GRAPH_COMPLETION) | Easy (Cypher pattern match) | No |
| Simple to set up for POC | Yes | Medium | Medium | Yes |

### The Key Insight

**Your data is relational AND semantic.** The decision trees only make sense when retrieved together with their required tools and evidence. This is genuinely a graph problem.

- **If you only need items individually** (search for "what does UNPROVISIONED mean?" → return the state_definition): any vector DB or Postgres works.
- **If you need diagnostic packages** (search for "service stuck" → return the matching decision tree + its tools + its evidence + its related states): you need graph traversal.

Your retrieval contract described in 02-retrieval-and-tool-binding.md implicitly requires the second pattern. The agent needs the decision tree AND the tool contracts it references to execute the diagnostic loop.

---

## 5. Practical Recommendation

### For Cognee Specifically

Cognee CAN work for this, but you would use it in a non-standard way:

**What you'd use:**
- Cognee's graph engine (Kuzu) for storing nodes + edges
- Cognee's vector engine (LanceDB) for semantic search on `statement` fields
- Cognee's `DataPoint` model extended with your custom fields
- Cognee's `GRAPH_COMPLETION` search mode to traverse from a matched node to its neighbors

**What you'd skip:**
- The `cognify` pipeline entirely (your knowledge is already structured)
- LLM-based entity extraction (you ARE the entity extractor)

**What you'd need to build on top:**
- Custom DataPoint subclasses for each knowledge type
- Custom ingestion script to load YAML items + edges
- Hard-filter-then-semantic-search retrieval function
- "Diagnostic package assembler" that follows edges after initial match

### My Updated Assessment

Given what's actually in this file, **Cognee is a reasonable choice** if you accept that you're using it as graph+vector infrastructure, not as an auto-extraction engine.

But the honest comparison is:

| Path | Time to first working retrieval test | Maintenance complexity |
|---|---|---|
| YAML files + Python script (in-memory) | 1-2 days | Low but doesn't scale |
| Cognee custom DataPoints | 3-5 days | Medium, leverages existing infra |
| Neo4j + vector index | 3-5 days | Medium, best native graph |
| Postgres + pgvector | 2-3 days | Low, but graph traversal is painful |

### Suggested First Step (Same Regardless of Backend)

1. Extract 10-15 items from the prompt file into YAML (covering: 2 scope rules, 3 state definitions, 2 decision trees, 2 tool contracts, 1 failure pattern, 1 evidence pattern)
2. Define the edges between them explicitly
3. Write 3 test scenarios with expected "diagnostic packages"
4. THEN load into your chosen backend and test retrieval

The YAML extraction is the same work no matter what. Start there.
