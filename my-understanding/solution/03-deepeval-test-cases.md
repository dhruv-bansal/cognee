# 03 - DeepEval Test Cases for Retrieval & Tool Selection

## Objective
To ensure the transition from prompt-embedded knowledge to the V1 structured knowledge model is successful, we must write automated evaluations using the DeepEval framework. These evaluations must verify both **Semantic/Metadata Retrieval** and **MCP Tool Selection Accuracy**.

## Test Case 1: Metadata-Aware Retrieval Accuracy (Stage 1)
This test ensures the orchestrator successfully filters by tenant/environment metadata, preventing cross-tenant leakage of provisioning rules.

### Setup (DeepEval Test Case)
1.  **Mock Database:** Populate Cognee/Graph store with 3 decision trees:
    *   `rule_mesh_escalation_tenant_a` (Tenant: `A`)
    *   `rule_standard_mesh_escalation` (Tenant: `all`)
    *   `rule_mesh_escalation_tenant_b` (Tenant: `B`)
2.  **Input Context:** User prompt: "Customer has a pending mesh node issue." Session Metadata: `tenant_id = B`, `environment = production`.
3.  **Action:** Trigger the "Retrieval Contract" function to query the knowledge graph.

### Assertions (DeepEval Metrics)
Using DeepEval's `ContextualPrecisionMetric` and `ContextualRecallMetric`:
*   **Assertion 1 (Precision):** Assert the returned context *includes* `rule_mesh_escalation_tenant_b` and `rule_standard_mesh_escalation`.
*   **Assertion 2 (Data Leakage/Negative Test):** Assert the returned context *does not include* `rule_mesh_escalation_tenant_a` (Tenant A).

## Test Case 2: Tool Selection Accuracy (Stage 2)
This test evaluates the LLM's ability to comprehend the injected `decision_tree` and `tool_contract` and output the correct MCP tool call sequence.

### Setup (DeepEval LLM Trace Evaluation)
1.  **Mock Context Injection:** Inject the exact JSON output of `rule_mesh_offline_escalation_v1` and `tool_contract_mesh_state_v1` into the LLM prompt.
2.  **Mock MCP Tools:** Provide the LLM with the MCP schema for `get_service_details_by_service_id` and `get_resource_by_cpe_id`.
3.  **Input Context:** User prompt: "Customer 123 is complaining their mesh node isn't working."
4.  **Action:** Request the next action from the LLM.

### Assertions (DeepEval Metrics)
Using DeepEval's `AnswerRelevancyMetric` or custom trace assertions:
*   **Assertion 1 (First Tool Call):** Assert the LLM's first generated output is a function call to `get_service_details_by_service_id` with parameter `service_id=123`.
*   **Assertion 2 (No Premature Execution):** Assert the LLM *does not* output a final answer or escalate the issue *before* receiving the mock response from the first tool call.

## Test Case 3: End-to-End Decision Resolution
This tests the full loop: Static Knowledge + Mocked Live State = Correct Final Action.

### Setup
1.  **Mock State Response:** When the LLM calls `get_service_details_by_service_id`, mock the response as `{"status": "PENDING"}`.
2.  **Mock Second Call:** When the LLM subsequently calls `get_resource_by_cpe_id`, mock the response as `{"status": "OFFLINE"}`.

### Assertions
*   **Final Decision Validation:** Assert the LLM outputs a final decision to "Escalate immediately to human operator," explicitly citing `rule_mesh_offline_escalation_v1` as the reason.
