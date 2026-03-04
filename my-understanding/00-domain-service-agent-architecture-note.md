# 00 - Domain + Service Agent Architecture Note

## Current Context (Updated)

- Agent orchestration stack: Google ADK.
- Target direction: self-healing system where domain/service agents can eventually change system state.
- Safety control: human-in-the-loop approval will be mandatory for state-changing actions.

## Business Problem (Restated)

You want to build a multi-agent backend where:

1. 50+ domain agents each own a bounded context (DDD style).
2. Domain agents use domain memory plus live enterprise tools through MCP (logs, DB, observability, legacy APIs, etc.).
3. A service agent orchestrates domain agents to solve cross-domain tasks such as production diagnosis, RCA, fix suggestions, and eventually code-level changes.
4. The same backend should support future interfaces (voice/avatar) and autonomous workflows (for example test generation and E2E validation).

## Is Cognee The Best Choice?

Short answer: Cognee is a strong choice for the shared memory layer, but not the full multi-agent platform by itself.

Why it fits this use case:

- You need relationship-aware memory across many domains, not only chunk similarity.
- You need long-term evolving memory (runbooks, incidents, architecture, policy).
- You need query modes for evidence, relationships, and timelines (`CHUNKS`, `GRAPH_COMPLETION`, `TEMPORAL`).
- You need to avoid prompt-only knowledge files that become stale.

Why it is not enough alone:

- Agent orchestration (planner/executor, delegation, retries, policy) still needs an orchestration layer (ADK/LangGraph/custom).
- Live system access and actions come from MCP tools, not from Cognee itself.
- Production guardrails (RBAC, approvals, sandboxing, change management) must be implemented outside Cognee.

Conclusion:

- If your key challenge is shared, cross-domain, relationship-heavy memory, Cognee is one of the best fits in your current stack direction.
- Treat it as memory infrastructure inside a larger agent platform, not as the whole platform.

## Recommended Architecture

### 1) Agent Roles

- Domain agents: own bounded context knowledge and local tool policies.
- Service agent: decomposes requests, delegates to domain agents, composes final result.
- Optional verifier agent: validates evidence quality, conflict resolution, and action safety.

### 2) Knowledge and Data Flow

- Curated knowledge (docs, architecture notes, postmortems, runbooks) is ingested into Cognee.
- High-volume runtime signals stay in observability systems; periodic summaries and derived facts are written into Cognee.
- Domain memory should be segmented by datasets/node sets per bounded context.

### 3) Tooling Flow (MCP)

- MCP provides runtime tools (logs, traces, DB read, ticketing, deployment state, legacy APIs).
- Domain agents pull live evidence through MCP.
- Service agent asks Cognee for historical/relational context and MCP for current state, then merges both.

### 4) Retrieval Routing

- "What changed before incident X?" -> `TEMPORAL`
- "How are service A and dependency B related?" -> `GRAPH_COMPLETION` or `TRIPLET_COMPLETION`
- "Show exact evidence" -> `CHUNKS`
- Default mixed reasoning -> `GRAPH_COMPLETION`

### 5) Action Safety and Change Path

- Separate phases: diagnose -> propose fix -> simulate/test -> approve -> apply.
- Keep code changes behind approval gates and CI checks.
- Record evidence links and decision trace for each recommendation.

## How This Solves Your Example Use Cases

### Production diagnosis and RCA

- Service agent delegates by suspected domain boundaries.
- Each domain agent returns: likely cause, confidence, evidence, missing data.
- Service agent fuses results and asks verifier for contradiction checks.
- Output includes RCA graph, timeline, and fix options.

### Suggesting or applying code fixes

- After RCA, generate candidate patches scoped to impacted services.
- Run local/static checks and targeted tests.
- Require approval before merge/deploy actions.

### Voice/avatar frontend in future

- Interface layer changes, but backend remains the same.
- Voice agent becomes another client of the same service-agent + domain-agent + memory/tool stack.

### E2E testing automation

- Agents use domain memory for expected behaviors and known failure patterns.
- Service agent composes multi-domain test plans.
- Results and regressions are written back as new memory facts.

## What To Implement First (Pragmatic Sequence)

1. Pick 3 to 5 high-value domains, not 50 at once.
2. Define dataset boundaries and access policy per domain.
3. Stand up one service agent orchestration loop with strict evidence format.
4. Integrate 2 to 3 MCP tools first (logs + read-only DB + traces).
5. Build an evaluation set for diagnosis tasks before enabling fix actions.

## Architecture Question Tracker ([ ] Open, [x] Closed)

- [x] 1. What is the authority boundary for each domain agent (read-only vs action-capable)?
Current answer: agents can eventually become action-capable through MCP; for state-changing actions, human-in-the-loop approval will be enforced via Google ADK flows.

- [ ] 2. What is the conflict-resolution rule when two domain agents disagree?
Current answer: still open; strategy is not finalized yet.

- [ ] 3. What confidence threshold triggers human escalation?
Current answer: still open; best strategy to be defined.

- [ ] 4. What approval workflow is required before code or infra changes?
Current answer: approval workflow will be implemented, but the main immediate focus is knowledge strategy (domain knowledge, learnings, chat history, effective add/retrieve, and context maintenance).

- [x] 5. How will tenant/environment isolation be enforced in memory and tools?
Current answer: in the current non-agentic system, tenant isolation is done via separate storage per tenant; application layer is common and stateless.

- [ ] 6. What data retention policy applies to memory from incidents and logs?
Current answer: still open; best strategy to be defined.

- [ ] 7. How often should runtime telemetry be summarized into Cognee memory?
Current answer: still open; best strategy to be defined, and overall solution choice (Cognee vs alternatives) is still under evaluation.

- [x] 8. Which agent owns cross-domain entities (for example shared platform services)?
Current answer: currently out of scope for this exercise.

- [x] 9. What is the rollback strategy if an auto-generated fix causes regression?
Current answer: currently out of scope for this exercise.

- [ ] 10. What are your target SLOs for diagnosis latency and answer quality?
Current answer: current priority is answer quality and accuracy; latency targets will be defined later.

## Decision Statement

Given your described business problem, use Cognee as the shared relationship-aware memory layer plus MCP-based live tools, orchestrated by a service-agent layer. This is a strong architectural fit, with the main risk area being governance and operational control rather than memory capability.
