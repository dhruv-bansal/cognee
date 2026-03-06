# Agent Quick Start for `my-understanding`

This file is the end-to-end handover entrypoint for any agent working in `my-understanding`.

## Problem Statement

Current domain knowledge for agents (especially provisioning) is heavily embedded in prompt files.
This makes knowledge hard to manage, evolve, validate, and retrieve consistently as the agent ecosystem scales.

## Core Architectural Principle: Generic Domain Knowledge, Not Playbooks

### The Problem With Playbooks

Today, domain knowledge is authored as **prescriptive playbooks**: "if you see state X and condition Y, do Z."
These playbooks work for known scenarios but fail fundamentally in production because:

1. **They are finite.** You can only diagnose problems someone already anticipated and wrote a decision tree for.
2. **They don't generalize.** A novel issue (never seen before, no matching decision tree) leaves the agent with nothing to work with.
3. **They are brittle.** When the system changes (new states, new tools, new components), every affected playbook must be manually updated.
4. **They don't scale.** At 50+ domains with evolving business processes, maintaining hand-authored playbooks for every scenario is not viable.

### The Right Approach: Domain Knowledge for Reasoning

Domain agents should own **generic domain knowledge** about how their business domain works, not pre-baked answers for specific use cases. The knowledge should enable the agent to **reason** about any problem, including ones never seen before.

What domain knowledge means:

- **What states exist and what they mean.** ("UNPROVISIONED means waiting for post-provisioning, not deactivated.")
- **How state transitions work and what triggers them.** ("UNPROVISIONED → PROVISIONED requires ACS success + PPPOE_RESET event.")
- **What tools are available and what they reveal.** ("get_service_details returns serviceState, cpeId, locks.")
- **How system components interact.** ("Pre-provisioning publishes CPEProvisioningEvent; post-provisioning consumes it when device is online.")
- **What invariants and constraints govern the domain.** ("RDK provisioning is async; LEGACY is sync." "There is no explicit OFFLINE state.")

Given this knowledge, the agent should be able to **derive** the correct diagnosis, action, or answer for any problem, including:

- Known scenarios (equivalent to following a decision tree, but reasoned rather than looked up)
- Novel scenarios (new failure modes, edge cases, system changes the author never anticipated)
- Cross-domain scenarios (combining knowledge from provisioning + networking + device management)

### How This Differs From Traditional RAG / Playbook Retrieval

| Approach | What is retrieved | What the agent does | Handles novel problems? |
|---|---|---|---|
| Full prompt (current) | Everything, always | Follows embedded decision trees | Only if a tree exists |
| Playbook retrieval | The matching pre-baked answer | Follows the retrieved playbook | No |
| **Domain knowledge retrieval** | **How the system works** | **Reasons from first principles** | **Yes** |

### What This Means for the Solution

1. **Knowledge modeling** must focus on extracting the domain's building blocks (states, transitions, flows, tools, constraints), NOT on authoring pre-computed diagnostic paths.
2. **Pre-baked decision trees** should become **test cases**, not agent input. They define expected reasoning outcomes that validate the agent can reach the right conclusion from domain knowledge alone.
3. **Retrieval** must assemble relevant domain context for the problem at hand, not match to a known scenario.
4. **Evaluation** must test reasoning quality: given domain knowledge + a novel problem, does the agent produce a correct, evidence-backed diagnosis?

### How Retrieval Works at Scale: Agent-Driven, Not Pre-Computed

A critical design decision: retrieval is NOT a pre-processing step that happens before
the agent runs. At 50+ domains with hundreds of knowledge items per domain, no system
can pre-compute exactly what knowledge the agent will need.

Instead, **the agent drives retrieval itself.** The knowledge store is exposed as a
tool (like any MCP tool). The agent queries it iteratively during reasoning:

1. Agent hears the problem and queries the knowledge store for initial understanding
   (e.g., "what does UNPROVISIONED mean?" or "what tools check provisioning state?")
2. Agent calls MCP tools to get live system state
3. Agent queries the knowledge store again based on what it observes
   (e.g., "what does PENDING_PPPOE_RESTART mean?" or "what transitions apply to UNPROVISIONED?")
4. Agent reasons with the accumulated domain knowledge + live evidence

This scales because:
- Each query is scoped (by domain, by type, by keywords) -- returns a small focused set
- Adding new domains or new knowledge doesn't require code changes
- Novel problems are handled because the agent can search by natural language
- The agent only pulls what it needs, not the entire domain

The knowledge store must support: metadata filtering (domain, type, tenant) +
semantic search (natural language queries on statements) + structured field match
(exact state values). Any backend supporting filtered semantic search works
(Postgres+pgvector, Cognee, Qdrant, etc.).

### Implications for Solution Design

All solution work in this exercise follows from this principle. The sequence is:

1. Extract generic domain knowledge from prompt files (states, transitions, tools, flows, constraints).
2. Model it in a structured, manageable, retrievable form.
3. Load it into a store that supports filtered semantic search.
4. Expose the store as a tool the agent can query during reasoning.
5. Convert existing decision trees into a test suite that validates reasoning quality.
6. Evaluate end-to-end: does the agent query the right knowledge and reason correctly?

## Overall Goal

Build a practical knowledge-first architecture where:

- generic domain knowledge (how systems work, not what to do for specific cases)
- conversation history
- learnings
- other reusable knowledge artifacts

are externalized, structured, retrievable, and maintainable with clear quality checks.

The architecture must enable domain agents to **reason** about any problem in their domain,
not just retrieve pre-baked answers for anticipated scenarios.

## Detailed Exercise Summary

This exercise aims to:

1. Understand current platform + agent + eval implementation as-is.
2. Identify what is currently acting as domain knowledge in production behavior.
3. Define concrete knowledge modeling decisions (starting with provisioning domain).
4. Establish practical rules for add/update/remove/retrieve of knowledge.
5. Keep non-knowledge architecture topics deferred until knowledge foundation is stable.


## Start Here (Read in Order)

1. Current implementation understanding summary:
[ current-agent-code-understanding/README.md ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/README.md)

Note:
The current platform/agents/evals understanding is already summarized under `current-agent-code-understanding/`. Do not re-discover from scratch unless explicitly asked.

2. Active decision tracker and open questions:
[ current-agent-code-understanding/questions.md ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/questions.md)

3. Current provisioning knowledge model baseline:
[ current-agent-code-understanding/09-provisioning-knowledge-model-v1.md ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/09-provisioning-knowledge-model-v1.md)

4. Solution landscape references:
- Potential solution path: `cognee/` folder
[ my-understanding/cognee ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/cognee)
- Other solution options:
[ agent-memory-solution-options.md ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/agent-memory-solution-options.md)

5. Business-problem architecture note:
[ 00-domain-service-agent-architecture-note.md ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/00-domain-service-agent-architecture-note.md)

6. Solution approach and evolution:
[ solution/00-approach-and-evolution.md ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/solution/00-approach-and-evolution.md)

7. Solutions (read in order):
- Solution 1 (playbook retrieval - superseded):
[ solution/solution-1-rule-based-retrieval/ ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/solution/solution-1-rule-based-retrieval/)
- Solution 2 (domain knowledge for reasoning - current):
[ solution/solution-2-domain-knowledge-reasoning/ ](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/solution/solution-2-domain-knowledge-reasoning/)


## Existing Elements Involved

Primary repositories in scope:

- framework/platform: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/platform`
- agents: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/agents/onebb-backend/agents`
- evals: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/evals`

Current runtime components:

- Google ADK + A2A communication
- Agent Registry
- Planner -> execution plan -> Executor contract (via shared session state)
- Domain agents: Provisioning Manager and Wifi Mesh
- Prompt Hub instruction files (major current knowledge source)
- MCP tools for logs/db/service/resource operations
- Session DB and resumability
- Evals (currently focused mostly on planner/executor behaviors)

Current prioritized domain for knowledge modeling:

- Provisioning domain knowledge extracted from prompt instructions first

## Current Priority Focus

Until changed explicitly, prioritize knowledge-building topics:

- domain knowledge
- conversation history
- learnings
- other reusable knowledge artifacts

When a question is outside this focus, mark it deferred instead of expanding scope.

## Status Notation (Mandatory)

Use these markers in question trackers:

- `[ ]` Open
- `[x]` Closed
- `[-]` Deferred

For each tracked question, include:

- a clear `Answer:` block when information is available
- status update based on that answer (`[ ]` -> `[x]` or `[-]`)

## Answer Preservation Rule (Mandatory)

- Do not delete user-provided answers.
- You may format, reorganize, or normalize wording for clarity, but preserve original intent.
- If an answer is partial, keep it and add follow-up questions instead of replacing it.

## Follow-up Numbering Rule

- Keep the parent question number unchanged.
- Add follow-up questions using hierarchical numbering:
1. `18.1`
2. `18.1.1`
3. `18.2`
- Use this pattern whenever deeper clarification is required.

## Deferral Rule

Mark as `[-] Deferred` when:

- question is valid but outside current focus
- decision is intentionally postponed
- dependency decision is not yet ready

Do not delete deferred questions. Keep them visible for future reopening.

## Documentation Conventions

- Keep files short, structured, and easy to scan.
- Prefer one topic per file.
- Keep implementation references concrete (file paths, module names, runtime behavior).
- Record assumptions explicitly.
- Keep questions in tracker format with status notation.
- Link new docs from relevant index files when adding content.

## Working Boundaries

- Treat external repos as read-only unless explicitly asked to modify.
- For this workspace, update only `my-understanding` docs unless told otherwise.
- If code appears locally inconsistent/uncommitted, document uncertainty rather than forcing conclusions.

## Suggested Workflow for New Work

1. Read the "Start Here" documents first.
2. Continue from existing summaries before opening raw code.
3. Add/update understanding docs with concrete evidence.
4. Update question tracker with `Answer:` and status.
5. Keep non-focus items deferred.
