# 00 - Solution Approach and Evolution

## Why This Document Exists

This document captures the thought process behind the solution approach: what we tried,
what we learned, and why the approach evolved. Read this before diving into any
specific solution folder.

## The Business Problem (Restated)

We have domain agents that need to handle complex business process problems (diagnosis,
provisioning, troubleshooting). Today all domain knowledge lives in prompt files. This
works when one prompt fits in one context window, but will not scale to:

- 50+ domains with evolving business processes
- Knowledge that can't fit in one prompt or one context window
- Novel production issues that nobody pre-anticipated
- Cross-domain reasoning that requires combining knowledge from multiple domains

## The Question We're Answering

**How do we model domain knowledge so that an agent can reason about any problem in its
domain -- including problems never seen before -- using selectively retrieved knowledge
instead of the full prompt?**

## Approach Evolution

### Approach 1: Playbook Retrieval (Solution 1 - Superseded)

**Idea:** Extract the decision trees and diagnostic playbooks from the prompt file into
structured YAML items. At runtime, match the user's problem to the right playbook and
inject it into the agent's context.

**What we built:** 27 knowledge items including pre-baked decision trees (DT#1 through
DT#8), plus their linked tool contracts, state definitions, and evidence patterns.
Rule-based retrieval matched scenarios to the right decision tree. Eval showed 7/7
scenarios passing.

**Why it was superseded:**

The decision trees ARE the diagnosis. Retrieving them is just a more structured way of
doing what the full prompt already does. This approach has three fundamental problems:

1. **Finite coverage.** It only works for problems someone already wrote a decision tree for.
   A novel production issue (first-time failure, unexpected state combination) has no
   matching playbook, so the agent has nothing to work with.

2. **Not actually knowledge.** Decision trees are pre-computed reasoning paths, not
   domain knowledge. They encode "if X then Y" without explaining WHY. The agent can't
   generalize from a playbook because it doesn't understand the system -- it just
   follows instructions.

3. **Doesn't scale.** At 50+ domains, maintaining hand-authored playbooks for every
   possible scenario is not viable. The whole point of having an AI agent is that it
   should reason, not just look things up.

**What we kept:** The extraction format (YAML with metadata), the test scenario structure,
and the eval harness concept all carry forward. Solution 1 is preserved as a reference.

### Approach 2: Domain Knowledge for Reasoning (Solution 2 - Current)

**Idea:** Instead of extracting pre-baked answers, extract the domain's building blocks:
how the system works. Give the agent knowledge to reason WITH, not answers to look UP.

**Core insight:** A senior engineer doesn't follow decision trees. They understand how
the system works (states, transitions, dependencies, tools) and reason about what's
broken from the evidence. Domain agents should work the same way.

**What changes:**

| Aspect | Solution 1 (Playbook) | Solution 2 (Domain Knowledge) |
|---|---|---|
| What is extracted | Decision trees, failure patterns | States, transitions, flows, tools, constraints |
| What agent receives | "If X and Y, do Z" | "Here's how the system works" |
| What agent does | Follows the playbook | Reasons about the problem |
| Novel problems | Fails (no matching playbook) | Reasons from first principles |
| Decision trees | Input to the agent | Test cases to validate reasoning |

**Knowledge types for reasoning (what we model):**

| Type | What it captures | Why the agent needs it |
|---|---|---|
| `state_definition` | What states exist and their meaning | To understand current system state |
| `transition_rule` | How states connect, what triggers transitions | To reason about what should have happened and what went wrong |
| `system_flow` | How components interact, message flows | To trace the path of an operation |
| `tool_contract` | What tools exist, what they reveal | To know how to gather evidence |
| `constraint` | Rules that are always true | To avoid incorrect reasoning |

**What becomes test cases (not agent input):**

| Type | Why it's a test case |
|---|---|
| `decision_tree` | Defines expected reasoning output: given this problem + domain knowledge, does the agent reach this diagnosis? |
| `prescriptive_failure_pattern` | Same: defines expected root cause identification |

## How the Knowledge Model Follows From This Principle

The knowledge model is NOT a taxonomy of document types. It is a model of how the
business domain works, structured so that an LLM can reason over it.

The modeling question is always: **"Does this piece of knowledge help the agent
understand the domain well enough to reason about a novel problem?"**

- If yes: it's domain knowledge. Extract it.
- If no: it's either behavioral instruction (stays in prompt) or a pre-baked answer
  (becomes a test case).

## How Retrieval Follows From This Principle

Retrieval does NOT match "problem → playbook." It assembles domain context:

1. **Identify the domain** from the user's problem (provisioning, wifi, etc.)
2. **Identify the entities involved** (service, resource, states mentioned)
3. **Retrieve relevant building blocks**: state definitions for mentioned states,
   transition rules that connect them, system flows they're part of, tools that can
   provide evidence, constraints that govern behavior.
4. **Assemble into agent context**: "Here's how this part of the system works.
   Here's the current state. Reason about what's wrong."

The agent then reasons, potentially:
- Following the same path a decision tree would (for known scenarios)
- Deriving a new path (for novel scenarios)
- Combining knowledge from multiple areas (for complex scenarios)

## How Evaluation Follows From This Principle

The eval question is NOT "did we retrieve the right playbook?" It is:

**"Given domain knowledge + this problem, does the agent reason to the correct diagnosis?"**

The decision trees from the prompt file become the golden test set:
- Each decision tree defines a scenario + expected diagnosis
- The test gives the agent only domain knowledge (states, transitions, tools, constraints)
- The assertion is: did the agent arrive at the same conclusion the expert encoded
  in the decision tree?

If the agent can match the expert's reasoning using only domain building blocks,
the knowledge model is sufficient. If it can ALSO handle novel scenarios the expert
didn't anticipate, the architecture works.

## How Retrieval Works at Scale: Agent-Driven Retrieval

### The Problem With Pre-Computed Retrieval

Solution 2's retrieval function (`retrieve_domain_knowledge`) analyzes tool responses
and returns relevant knowledge items. This works for testing the knowledge model, but
at scale (50 domains, hundreds of items per domain), you cannot pre-compute what the
agent needs. Two reasons:

1. **Before tools are called**, you don't know the system state, so you can't decide
   which state definitions, transitions, or constraints are relevant.
2. **During reasoning**, the agent may discover new questions that require additional
   knowledge it didn't know it needed initially.

### The Solution: Knowledge Store as an Agent Tool

At production scale, the knowledge store is exposed as a tool the agent can query
during reasoning -- just like it queries MCP tools for live system state.

**Runtime flow:**

```
User problem
    │
    ▼
Agent queries knowledge store: "What tools exist for provisioning?"
    → Gets tool contracts
    │
    ▼
Agent calls MCP tools (get_service_details, get_resource)
    → Gets live state
    │
    ▼
Agent queries knowledge store: "What does PENDING_PPPOE_RESTART mean?"
    → Gets state definition + transitions + constraints
    │
    ▼
Agent reasons with domain knowledge + live evidence → Diagnosis
```

The agent drives retrieval iteratively. Each query is scoped and returns a small set.
The total knowledge consumed is proportional to the problem complexity, not to the
domain size.

### What the Knowledge Store Must Support

The store needs three search capabilities:

1. **Metadata filtering**: `domain=provisioning, type=constraint, status=active`
2. **Semantic search**: `query="device not coming online after provisioning"`
3. **Structured field match**: `entity=service, value=UNPROVISIONED`

Combined: `domain=provisioning, type=transition_rule, query="what triggers PROVISIONED"`

This is a filtered semantic search problem. Suitable backends: Postgres+pgvector,
Cognee (with custom queries), Qdrant, Weaviate, Neo4j+vector index.

### What This Means for Evaluation

The test question becomes: **"Given a `search_knowledge` tool + MCP tools + a problem,
does the agent query the right knowledge and reason to the correct diagnosis?"**

```yaml
test:
  available_tools: [search_knowledge, get_service_details, get_resource, search_logs]
  knowledge_store: [all 31 domain knowledge items]
  user_input: "Service 12345 stuck in UNPROVISIONED"
  assertions:
    - agent queried knowledge store before or alongside MCP tools
    - agent retrieved relevant state definitions and transitions
    - agent diagnosis matches expected conclusion
    - agent did not fabricate knowledge it didn't retrieve
```

### What This Means for the Backend Decision

The backend choice is no longer deferred -- it follows directly from the search
requirements. Any backend that supports filtered semantic search is viable.
The evaluation should test with a real backend to validate search quality.

## Decision Log

| Decision | Date | Rationale |
|---|---|---|
| Start with provisioning domain | Pre-existing | Richest prompt file, most structured domain knowledge |
| Solution 1: playbook retrieval | 2026-03-04 | First attempt to validate extraction + retrieval mechanics |
| Solution 1 superseded | 2026-03-04 | Playbook retrieval doesn't handle novel problems, doesn't scale |
| Solution 2: domain knowledge for reasoning | 2026-03-04 | Aligns with how experts actually work, handles novel problems |
| Decision trees → test cases | 2026-03-04 | DTs define expected reasoning, not agent input |
| Agent-driven retrieval | 2026-03-04 | At scale, agent must drive its own knowledge retrieval via a search tool |
| Backend must support filtered semantic search | 2026-03-04 | Required by agent-driven retrieval pattern |
