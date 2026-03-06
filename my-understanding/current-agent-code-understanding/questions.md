# Functional Questions (Current Code Understanding)

These questions are based on current code behavior and are tracked with status notation.

## Current Focus

Current focus is knowledge-building strategy only:

- domain knowledge
- conversation history
- learnings
- other reusable knowledge artifacts

Questions outside this scope are intentionally deferred for now to keep decisions focused and avoid premature architecture branching.

## Status Notation

- `[ ]` Open
- `[x]` Closed
- `[-]` Deferred

## In-Scope Questions (Knowledge Focus)

- [x] 9. Which knowledge classes should remain prompt-embedded versus moved to external memory (runbooks, incidents, chat learnings, policies)?
Answer:
All business/operational knowledge should be externalized and managed as first-class knowledge assets.
Includes domain knowledge, learnings, summaries, feedback, and similar reusable knowledge.
This is the preferred direction for production use.

- [x] 10. Do you want Prompt Hub as central policy-only instructions, with domain facts moved out to memory retrieval?
Answer:
Yes, directionally. Prompt Hub can continue to exist for policy/behavior instructions while knowledge is moved to an external managed knowledge layer.
Main requirement is strong knowledge lifecycle control: add, update, remove, and retrieve the right knowledge at the right time based on intent/problem context.
Memory modeling approach is still open, but the goal (externalized, manageable knowledge) is clear.

## New Follow-up Questions (Knowledge Focus)

- [x] 18. What is the first formal knowledge taxonomy we should use (for example: domain_facts, runbooks, incident_rca, chat_history, learnings, feedback, decision_logs)?
User answer summary:
Externalize prompt-embedded knowledge first, then validate retrieval accuracy.
Decision (v1):
Use this taxonomy for Provisioning domain extraction:
1. `scope_rule` (in-scope/out-of-scope and mandatory identifier rules)
2. `state_definition` (service/resource/operational states and meanings)
3. `transition_rule` (state transitions and triggers)
4. `decision_tree` (diagnostic branch logic)
5. `failure_pattern` (known failure signatures + probable causes)
6. `evidence_pattern` (what evidence confirms/rejects a hypothesis)
7. `tool_contract` (tool purpose, required inputs, expected outputs)
8. `workflow_step` (pre/post provisioning flow steps)
9. `reference_map` (microservice/component responsibilities)

- [x] 19. What should be the minimum metadata schema per knowledge item (tenant, environment, domain, source, timestamp, confidence, lifecycle status)?
User answer summary:
Metadata may differ by knowledge type.
Decision (v1):
Use one minimum common schema for all extracted knowledge:
`knowledge_id`, `domain`, `knowledge_type`, `title`, `statement`,
`preconditions`, `expected_outcome`, `source_file`, `source_section`,
`source_anchor`, `source_kind` (`prompt_table|prompt_text|code|chat|incident`),
`tenant_scope` (`global|tenant`), `environment_scope`, `version`,
`confidence`, `status` (`active|candidate|deprecated`), `tags`,
`created_at`, `updated_at`.

- [x] 20. What should be the write path for new knowledge (manual curation, automated summarization, agent-generated proposals with approval, or hybrid)?
User answer summary:
Could start from reverse-engineered markdown or direct code input.
Decision (v1):
Use hybrid write path with explicit precedence:
1. Baseline authoritative load: Prompt markdown extraction (current domain source of truth)
2. Enrichment load: Code-derived facts/tool contracts
3. Candidate load: Chat/incident learnings (not authoritative until approved)
Publish policy: `candidate -> reviewed -> active`.

- [-] 21. What freshness strategy should apply per knowledge class (real-time, hourly, daily, event-driven)?
Answer:
Deferred explicitly for now; focus is first on early knowledge extraction and retrieval quality.

- [x] 22. How should conversation history be transformed into durable knowledge (raw transcript vs summarized episodes vs extracted facts)?
User answer summary:
Current history is in Postgres via ADK; context quota idea exists.
Decision (v1):
Use 3-layer history model:
1. Raw session log (Postgres, operational only, not directly injected to long-term memory)
2. Episodic summary (session-level compressed memory)
3. Promoted facts/learnings (only after extraction + confidence check + optional approval)
Promotion rule: only durable facts/learnings move to active long-term knowledge.

- [x] 23. What is the retrieval policy contract for service/domain agents (top_k, filters, ranking, recency boost, confidence threshold)?
User answer summary:
Single policy is not sufficient; runtime selection preferred.
Decision (v1):
Use runtime-selectable retrieval profile with mandatory domain filter.
Contract:
1. Intent classification -> retrieval profile selection
2. Profile selects allowed knowledge types and per-type `top_k`
3. Ranking uses hybrid score (semantic + source authority + recency)
4. Confidence threshold gates final context inclusion
5. If confidence is low, route to clarifying/evidence expansion path

- [-] 24. What should be the conflict-resolution strategy when multiple knowledge items disagree (latest-wins, source-priority, confidence-weighted, human-review)?
Answer:
Deferred explicitly for now; to be addressed after initial knowledge extraction and retrieval-quality baseline.

- [-] 25. What retention and archival policy should apply for each knowledge class (short-term context vs long-term memory)?
Answer:
Deferred explicitly for now; to be addressed after initial knowledge extraction and retrieval-quality baseline.

- [x] 26. For first implementation, what should be the canonical ingestion source: reverse-engineered markdown knowledge docs, direct code ingestion, or both with precedence rules?
Decision (v1):
Use both with precedence:
1. Prompt markdown extraction (highest priority)
2. Code extraction for technical/tool details
3. Chat/incident learnings as candidate layer

- [x] 27. Should context quota be static (fixed percentages) or dynamic (intent/query-driven allocation at runtime)?
Decision (v1):
Use dynamic quota by intent/profile, with safety caps.
Default starting caps:
- domain knowledge: 40-60%
- case history/episodes: 20-30%
- live tool evidence: 20-40%

## Deferred Questions (Out of Current Scope)

- [-] 1. Are `NetworkAgent` and `PlayerAgent` part of another repo/runtime, or planned but not yet integrated here?
- [-] 2. What is the source-of-truth list of production agents today (including domain vs service tags)?
- [-] 3. Is `execution_plan` in custom session DB the long-term contract, or temporary until a different orchestration state store is introduced?
- [-] 4. Should executor fail fast if `REMOTE_AGENT_CONFIG` is missing/invalid, instead of silently using `{}`?
- [-] 5. Should QuerySense always run first for every request, or only for cold-start/no-context sessions?
- [-] 6. Should QuerySense remain pure classifier/gate, or also collect mandatory IDs per domain?
- [-] 7. Should every domain agent follow two-stage Investigator/Challenger design like ProvisioningManager, or is single-agent acceptable by default?
- [-] 8. Do you want a required domain-agent template (tools, memory, validation, output schema) for future 50+ agents?
- [-] 11. What are the exact classes of actions that must always go through explicit human approval?
- [-] 12. Should approval happen at planner stage, executor stage, or inside each domain agent before tool invocation?
- [-] 13. Is tenant/environment metadata guaranteed for all entry channels (not just Magnus path)?
- [-] 14. Should authorization token always be propagated into downstream A2A and MCP calls, or only selected tools?
- [-] 15. Should next eval phase include domain-agent quality benchmarks (Provisioning/Wifi) in addition to planner/executor control metrics?
- [-] 16. Do you want evals to validate tool-groundedness against real MCP responses, or stay simulation-first initially?
- [-] 17. Should we clean and align repo metadata (agent list, README completeness, env schema consistency) as a separate hardening task before scaling?
