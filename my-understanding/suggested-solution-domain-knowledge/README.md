# Suggested Solution: Practical Domain Knowledge Retrieval With Google ADK

## Why This Document Exists

This is the practical suggested solution for the current business problem:

- domain knowledge is growing and should not stay embedded in prompts
- agents must retrieve the right amount of knowledge, not the whole domain
- agents must combine static domain knowledge with live MCP evidence
- we need confidence that retrieval is correct before scaling to many domains

This document is intentionally practical. It is not trying to design the final perfect platform.
It defines a confidence-building V1 that still aligns with the longer-term architecture.

## Recommended Decision

Use this architecture direction:

- **Google ADK** remains the agent orchestration framework
- **MCP tools** remain the source of live operational state
- **External domain knowledge store** becomes the source of static business/domain knowledge
- **Memory Gateway** sits in front of the knowledge store and exposes controlled retrieval tools to agents
- **Evaluation harness** measures retrieval quality, sufficiency judgment, and grounded reasoning

## The Core Design Principle

Do not make the first problem "how do we chunk documents?"

The first problem is:

**What is the right unit of knowledge for reasoning?**

For this use case, the default unit should be a **knowledge item**, not a raw document chunk.

Examples:

- one `state_definition`
- one `transition_rule`
- one `tool_contract`
- one `constraint`
- one `workflow_step`
- one `reference_map`

This is a better fit for business-process reasoning than indexing only raw text chunks.

## Recommended Architecture

```text
User / Upstream Agent
        |
        v
Google ADK Service Agent
        |
        v
Google ADK Domain Agent
        |
        +--> Memory Gateway Tool(s)
        |       |
        |       +--> Knowledge Store
        |       |      - preferred target: Cognee
        |       |      - acceptable V1 backend: vector + metadata store
        |       |
        |       +--> Episode / Learning Store
        |
        +--> MCP Tools
                - DB read
                - logs
                - traces
                - service/resource APIs
```

## Why This Architecture

### 1. Keep ADK, do not replace it

You are already using Google ADK for:

- agent topology
- routing and delegation
- session state
- A2A communication

That is the orchestration layer. The missing piece is not orchestration. The missing piece is controlled domain-knowledge retrieval.

### 2. Do not let agents query the storage backend directly

Agents should not know or care whether memory is stored in:

- Cognee
- Postgres + pgvector
- Qdrant
- another backend later

Agents should call a stable retrieval tool contract exposed by a **Memory Gateway**.

### 3. Keep live state separate from durable knowledge

Static knowledge:

- how provisioning works
- what states mean
- what transitions should occur
- what tools are relevant
- what constraints govern behavior

Live state:

- current DB values
- current logs
- current traces
- current service/resource status

The workflow must be:

**retrieve static knowledge -> decide which MCP tools to call -> fetch live evidence -> reason**

Not:

**store current live system state in long-term memory and hope it stays correct**

## Backend Recommendation

### Recommended target direction

Use **Cognee** as the shared long-term relationship-aware memory layer.

Why:

- fits cross-domain and relationship-heavy business knowledge
- aligns with the direction already captured in `agent-memory-solution-options.md`
- supports a future where domains, learnings, incidents, and relationships matter more than plain text similarity

### Recommended implementation posture for V1

Do **not** couple agents directly to Cognee query modes yet.

Instead:

1. Define the retrieval tool contract first
2. Put a Memory Gateway in front of the backend
3. Start with one domain
4. Validate retrieval and eval quality
5. Then keep or replace the backend implementation behind the same gateway contract

This keeps the architecture stable while allowing backend experimentation.

## What To Store

### V1: domain knowledge for reasoning

Prioritize these knowledge types:

1. `state_definition`
2. `transition_rule`
3. `system_flow`
4. `tool_contract`
5. `constraint`
6. `workflow_step`
7. `reference_map`

Use these carefully:

- `failure_pattern`
  - allowed, but should support reasoning rather than act as a pre-baked answer

- `decision_tree`
  - keep primarily as evaluation goldens, not primary runtime retrieval input

### Conversation and learnings

Use a separate layered approach:

1. raw ADK/session history
2. episodic summaries
3. promoted learnings/facts

Only promoted learnings should become durable long-term memory candidates.

## Storage Strategy

### Primary storage unit

Store one atomic knowledge item per record.

Each item should include:

- `knowledge_id`
- `domain`
- `knowledge_type`
- `title`
- `statement`
- `entities`
- `preconditions`
- `expected_outcome`
- `source_file`
- `source_section`
- `tenant_scope`
- `environment_scope`
- `version`
- `confidence`
- `status`
- `tags`
- `created_at`
- `updated_at`

### What about chunking

Chunking is still useful, but not as the primary runtime model.

Use chunking only for:

- raw source ingestion
- long markdown/pdf parsing
- source traceability
- fallback text retrieval when structured extraction is incomplete

Recommended rule:

- **Structured knowledge items** are the main retrieval unit
- **Document chunks** are a support layer for provenance and extraction

### When hierarchical chunking is useful

If you ingest large manuals, process docs, or prompt markdown:

- use larger parent chunks for extraction context
- use smaller child chunks for source search and provenance lookup

But the runtime reasoning loop should prefer extracted knowledge items whenever possible.

## Memory Gateway: Required Tool Contract

The gateway should expose a small set of tools to ADK agents.

### 1. `search_domain_knowledge`

Purpose:
- retrieve static domain knowledge relevant to the current problem

Input:
- `domain`
- `query`
- `knowledge_types`
- `tenant_scope`
- `environment_scope`
- `top_k`
- `retrieval_profile`

Output:
- list of knowledge items
- score/rank
- reasons or matched fields
- `knowledge_id`

### 2. `get_knowledge_by_id`

Purpose:
- retrieve a full item when the agent already knows what it wants

### 3. `search_episode_memory`

Purpose:
- retrieve relevant prior incidents, summaries, or promoted learnings

This should be separate from domain knowledge retrieval. Do not mix the two blindly.

### 4. Optional `expand_related_knowledge`

Purpose:
- fetch directly related items by entity or edge

Useful later when relationship-heavy retrieval becomes important.

## Retrieval Policy Contract

This is the most important control layer.

### Hard filters first

Never rely on semantic search alone.

Always filter by:

- `domain`
- `tenant_scope`
- `environment_scope`
- `status = active`

### Retrieval profile second

Pick allowed knowledge types based on intent.

Examples:

- state explanation
  - `state_definition`, `constraint`

- diagnosis
  - `state_definition`, `transition_rule`, `constraint`, `tool_contract`, `system_flow`

- action planning
  - diagnosis profile + `workflow_step`

- prior similar case lookup
  - `search_episode_memory`, not only `search_domain_knowledge`

### Small initial retrieval set

Do not inject a large blob of knowledge.

Start with a small focused set:

- `top_k` per type
- context budget per retrieval profile
- explicit second retrieval only if needed

### Agent-controlled expansion, but bounded

The agent should be able to retrieve again if it still has gaps.

But the loop must be bounded by:

- max retrieval rounds
- max items per round
- allowed knowledge types per round

## Runtime Flow In Google ADK

### Step 1: service or planner layer routes to the domain

The ADK service/planner layer identifies:

- the likely domain
- whether this is diagnosis, explanation, planning, or cross-domain delegation

### Step 2: domain agent performs initial knowledge retrieval

The domain agent calls:

- `search_domain_knowledge(...)`

It gets a small set of items such as:

- relevant state definitions
- transition rules
- constraints
- tool contracts

### Step 3: domain agent chooses MCP tools

Using retrieved `tool_contract` and other knowledge, the agent decides which MCP tools to call.

Examples:

- `get_service_details`
- `get_resource`
- `search_logs`
- `fetch_trace_summary`

### Step 4: domain agent checks for knowledge gaps

After live evidence returns, the agent asks:

- do I understand the observed state?
- do I know the relevant transition rules?
- do I know the constraints that govern this scenario?
- do I know which further live evidence is required?

If not, it calls the Memory Gateway again with a more specific query.

### Step 5: final answer must declare sufficiency

Every final answer should include an explicit status:

- `enough_evidence`
- `partial_evidence`
- `insufficient_evidence`

This must be structured output, not just prose.

## Required Answer Contract

The domain agent should return a structured object like:

```json
{
  "answer_status": "partial_evidence",
  "summary": "The service appears stuck before the expected provisioning transition.",
  "used_knowledge_ids": [
    "prov_state_unprovisioned",
    "prov_transition_pppoe_reset",
    "prov_tool_get_service_details"
  ],
  "used_mcp_tools": [
    "get_service_details",
    "get_resource"
  ],
  "missing_information": [
    "No evidence confirming whether the post-provisioning event was published"
  ],
  "recommended_next_steps": [
    "Check event publication logs for CPEProvisioningEvent"
  ]
}
```

This is critical for trust. The agent must be able to say:

- I have enough evidence
- I have only part of the evidence
- I could not fetch the required knowledge

## Practical Confidence-Building V1

Do not start with 50 domains.

Start with:

- **one domain**
- **30 to 100 curated knowledge items**
- **one Memory Gateway tool**
- **2 to 4 MCP tools**
- **20 to 30 evaluation scenarios**

Best first domain:

- provisioning

Because:

- it already has prompt-embedded knowledge
- it already has clear tool interactions
- it already has usable golden scenarios

## Suggested Phased Delivery

### Phase 0: freeze the V1 target

Deliverables:

- domain chosen
- knowledge taxonomy agreed
- metadata schema agreed
- eval scenario template agreed

### Phase 1: build the knowledge corpus

Deliverables:

- extract provisioning knowledge from prompts
- normalize into atomic items
- load into the backend behind the Memory Gateway

Success criteria:

- knowledge can be added, updated, deprecated, and versioned

### Phase 2: build retrieval-only evaluation

Deliverables:

- test cases with expected `knowledge_id`s
- retrieval metrics:
  - precision
  - recall
  - irrelevant item rate

Success criteria:

- the retrieval system consistently fetches the needed items for known scenarios

### Phase 3: bind ADK domain agent to the gateway

Deliverables:

- ADK domain agent can call `search_domain_knowledge`
- agent chooses MCP tools after retrieval
- final response uses explicit sufficiency status

Success criteria:

- agent can reason from retrieved domain knowledge plus mocked live evidence

### Phase 4: add episodic memory and learnings

Deliverables:

- incident summary retrieval
- promoted learnings lifecycle
- candidate -> reviewed -> active flow

### Phase 5: add verifier and cross-domain composition

Deliverables:

- verifier step for evidence sufficiency
- service-agent composition across domains

## Evaluation Strategy

Confidence will come from evaluation, not from architectural elegance.

Use four evaluation layers.

### 1. Retrieval accuracy

Question:
- Did the Memory Gateway return the right knowledge items?

Measure:
- precision
- recall
- irrelevant item rate

### 2. Tool-selection quality

Question:
- Given the correct domain knowledge, did the agent call the right MCP tools?

Measure:
- tool choice correctness
- tool order correctness

### 3. Sufficiency judgment

Question:
- Did the agent correctly say `enough`, `partial`, or `insufficient`?

This is essential for your use case.

### 4. End-to-end reasoning

Question:
- Given domain knowledge + live evidence, did the agent reach the correct diagnosis or escalation?

## Suggested Evaluation Dataset Shape

For each scenario, define:

- `scenario_id`
- `domain`
- `user_problem`
- `expected_knowledge_ids`
- `disallowed_knowledge_ids`
- `mock_mcp_responses`
- `expected_tool_calls`
- `expected_answer_status`
- `expected_diagnosis`

This gives a clean bridge from retrieval quality to agent quality.

## What Not To Do In V1

- Do not expose all memory content directly to the prompt
- Do not let semantic search run without metadata filters
- Do not mix live state into durable memory
- Do not use raw decision trees as the primary runtime reasoning source
- Do not optimize for all domains before one domain is measurable
- Do not make the initial success criterion "the demo answer sounded good"

## Practical Recommendation Summary

If a single concrete recommendation is needed, it is this:

1. Keep **Google ADK** as orchestration
2. Use a **Memory Gateway** as the retrieval API boundary
3. Use **Cognee** as the preferred long-term backend target
4. Start V1 with **atomic knowledge items**, not chunk-first raw RAG
5. Keep **MCP** as the live-state source
6. Force the agent to output **evidence sufficiency status**
7. Build confidence through **retrieval and reasoning evals** before scaling

## Implementation Notes For The First POC

If the goal is simply to gain confidence quickly, the first POC should produce:

- a provisioning knowledge dataset
- a retrieval tool callable by an ADK domain agent
- mocked MCP tools
- a retrieval eval runner
- a domain-agent reasoning eval runner

That is enough to answer the real business question:

**Can this memory setup retrieve the right knowledge and help the agent reason correctly?**

If the answer is yes for one domain, then scaling and backend refinement become engineering work, not conceptual uncertainty.
