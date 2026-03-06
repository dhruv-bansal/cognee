# 01 - Knowledge Extraction Blueprint

## The Problem
Currently, all domain knowledge (playbooks, decision trees, RCA guidance) is heavily embedded directly into the prompt file `ProvisioningManagerInvestigator_Instruction.md`. This file acts as the "Prompt Hub" and is located directly in the platform codebase (specifically under the `onebb-backend/agents/provisioning-manager-agent` directory). 

This hardcoded approach makes versioning, tenant-specific logic, and structured retrieval impossible.

## The Strategy for Extraction and Management
We cannot just manually copy-paste this data once. We need a systematic migration strategy to move this knowledge from the static platform codebase into a dynamic, queryable graph (like Cognee).

### Phase 1: Markdown Parsing (The Extraction Pipeline)
1.  **Parse by Headers:** Build a utility script (e.g., in Python) to parse the `ProvisioningManagerInvestigator_Instruction.md` file. It will split the large document into logical chunks based on Markdown headers (`##`, `###`).
2.  **LLM-Assisted Classification:** Run each parsed chunk through an LLM to classify it against the V1 Taxonomy (`scope_rule`, `decision_tree`, `tool_contract`, `failure_pattern`).
3.  **JSON Transformation:** Convert the classified Markdown chunks into the strictly typed JSON schema defined below.

### Phase 2: Dual-Write Management (Migration)
During the transition, we must ensure we don't break the active platform:
1.  **Ingest to Graph:** The extracted JSON items are pushed to the Graph database (Cognee).
2.  **Truncate the Prompt:** Once verified in the Graph, we delete those specific sections from the `ProvisioningManagerInvestigator_Instruction.md` file in the platform repo.
3.  **Inject Retrieval:** We replace the deleted Markdown sections with a single instruction telling the agent to query its dynamic context window.

---

## Concrete Extraction Example

## Concrete Example: Converting a Decision Tree

Imagine the `ProvisioningManagerInvestigator_Instruction.md` currently contains the following text block:

> "If checking a mesh node provisioning failure, first use the `get_service_details_by_service_id` tool. If the state is 'PENDING', check the `get_resource_by_cpe_id` tool. If the physical CPE device is offline, escalate the provisioning task immediately."

### Extracted Knowledge Item (JSON/YAML Structure)
Here is how that exact text should be extracted and modeled in the new system (e.g., ingested into Cognee):

```json
{
  "knowledge_id": "rule_mesh_offline_escalation_v1",
  "domain": "provisioning",
  "knowledge_type": "decision_tree",
  "title": "Mesh Node Offline Escalation Path",
  "statement": "When a mesh node provisioning state is PENDING, verify the physical device connectivity status. If the CPE device is OFFLINE, the provisioning process must be escalated immediately without further automated retries.",
  "preconditions": [
    "service_type == 'mesh_node'"
  ],
  "expected_outcome": "Immediate escalation to human operator if the CPE device is offline.",
  "source_file": "ProvisioningManagerInvestigator_Instruction.md",
  "source_section": "Mesh Troubleshooting Playbook",
  "source_anchor": "line_45_to_50",
  "source_kind": "prompt_extraction",
  "tenant_scope": ["all"],
  "environment_scope": ["production", "staging"],
  "version": "1.0",
  "confidence": 0.95,
  "status": "active",
  "tags": ["mesh", "escalation", "offline", "cpe"],
  "created_at": "2023-10-27T10:00:00Z",
  "updated_at": "2023-10-27T10:00:00Z"
}
```

### Extracted Tool Contract (JSON/YAML Structure)
To ensure the agent knows *how* to verify the "PENDING" and "OFFLINE" states mentioned above, we also extract a `tool_contract` item.

```json
{
  "knowledge_id": "tool_contract_mesh_state_v1",
  "domain": "provisioning",
  "knowledge_type": "tool_contract",
  "title": "Tools required for Mesh State Check",
  "statement": "To verify a mesh node state, first call 'get_service_details_by_service_id' to check the provisioning state. To verify physical device connectivity, call 'get_resource_by_cpe_id'.",
  "preconditions": [
    "intent == 'verify_mesh_state'"
  ],
  "expected_outcome": "Service provisioning status and physical device (CPE) connectivity status.",
  "source_file": "ProvisioningManagerInvestigator_Instruction.md",
  "source_kind": "prompt_extraction",
  "tenant_scope": ["all"],
  "environment_scope": ["production", "staging"],
  "version": "1.0",
  "confidence": 1.0,
  "status": "active",
  "tags": ["tooling", "mesh", "status_check"]
}
```

## What Remains in the Prompt
After extracting all decision trees, failure patterns, and tool contracts into the structures above, the `ProvisioningManagerInvestigator_Instruction.md` prompt will be heavily reduced.

**It will only contain:**
1. **Persona/Role:** "You are the Provisioning Manager Investigator..."
2. **Behavioral Rules:** "Always cite the specific `knowledge_id` you used to make your decision."
3. **Safety Instructions:** "Do not execute state-changing MCP tools without explicit Human-in-the-Loop approval."
4. **Retrieval Contract Hook:** "Consult the retrieved context (injected below) to determine the specific rules and tools to apply for the current tenant and environment."