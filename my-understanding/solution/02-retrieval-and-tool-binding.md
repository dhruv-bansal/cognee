# 02 - Retrieval and Tool Binding Architecture

## The Challenge
Once we extract the domain knowledge into Cognee (or a similar graph/vector store), we need an orchestration mechanism that correctly retrieves the knowledge *and* strictly enforces the contextual quota. We then need the agent to use that static knowledge to dynamically select MCP tools to read live state.

## 1. The Retrieval Contract Execution

Before the `ProvisioningManager_Investigator` begins analyzing a request, the system must execute the Retrieval Contract.

### Step A: Intent & Metadata Filtering (Hard Filters)
The system must never rely on semantic search alone for enterprise knowledge. It must pre-filter the database based on the active session context:
- `domain` == "provisioning"
- `tenant_scope` contains active session tenant ID (or "all")
- `environment_scope` contains active session environment (e.g., "production")
- `status` == "active"

### Step B: The Context Quota Assembler
The retrieved items are assembled into the agent's context window. The system must enforce the V1 Quota:
1.  **Domain Knowledge (40-60% of context window):** The `decision_tree`, `scope_rule`, and `tool_contract` items retrieved from Cognee.
2.  **Case History/Episodes (20-30% of context window):** Summary of recent, similar incidents (pulled from Postgres session logs).
3.  **Live Tool Evidence (20-40% of context window):** Reserved space for the outputs of the MCP tools the agent will call next.

## 2. Binding Static Knowledge to Dynamic MCP Tools

The core of this architecture is separating "what to do" from "the current state". 

### The Execution Loop:

1.  **Retrieval Injection:** The agent receives the user prompt ("Customer X's mesh node is broken") along with the assembled context from Step B.
2.  **Knowledge Comprehension:** The agent reads the injected `decision_tree` (e.g., "If a mesh node provisioning is PENDING...").
3.  **Tool Contract Resolution:** The agent reads the injected `tool_contract` (e.g., "To verify mesh provisioning state, use `get_service_details_by_service_id`").
4.  **First MCP Call:** The agent outputs a command to call `get_service_details_by_service_id(service_id=Customer_X)`.
5.  **State Ingestion:** The MCP tool returns live state: `{"status": "PENDING"}`. This is appended to the "Live Tool Evidence" section of the prompt.
6.  **Second MCP Call (Chain):** The agent consults the `decision_tree` again, sees it must check if the device is offline, and calls the next tool: `get_resource_by_cpe_id(cpe_id=Y)`.
7.  **Final Decision:** The MCP tool returns `{"status": "OFFLINE"}`. The agent matches this against the `decision_tree` outcome ("escalate immediately if offline") and halts execution to ask for human escalation.

## 3. Why This Works
By explicitly defining `tool_contract` as a distinct knowledge type, we decouple the *definition* of an API/tool from the *logic* of when to use it. If the underlying API changes (e.g., `get_service_details` becomes `v2_service_lookup`), we only update the `tool_contract` item in the knowledge graph. The `decision_tree` items remain untouched.