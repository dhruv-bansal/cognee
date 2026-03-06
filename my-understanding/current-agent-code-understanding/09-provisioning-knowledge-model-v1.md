# 09 - Provisioning Knowledge Model v1

This is the concrete first model for domain knowledge extraction from provisioning prompt files.

## Goal

Extract prompt-embedded provisioning knowledge into structured, queryable knowledge items while keeping prompt files for behavior/policy.

## Source of Truth (v1)

Primary source:

- `ProvisioningManagerInvestigator_Instruction.md`

Secondary source:

- `ProvisioningManagerChallenger_Instruction.md`

## Taxonomy (v1)

Use these knowledge types:

1. `scope_rule`
2. `state_definition`
3. `transition_rule`
4. `decision_tree`
5. `failure_pattern`
6. `evidence_pattern`
7. `tool_contract`
8. `workflow_step`
9. `reference_map`

## Metadata Schema (Minimum)

Each knowledge item must include:

- `knowledge_id`
- `domain`
- `knowledge_type`
- `title`
- `statement`
- `preconditions`
- `expected_outcome`
- `source_file`
- `source_section`
- `source_anchor`
- `source_kind`
- `tenant_scope`
- `environment_scope`
- `version`
- `confidence`
- `status`
- `tags`
- `created_at`
- `updated_at`

## Write Path (v1)

Hybrid with precedence:

1. Prompt markdown extraction (authoritative baseline)
2. Code-derived enrichment (tool/technical details)
3. Chat/incident learnings as `candidate`

Publishing lifecycle:

- `candidate -> reviewed -> active`

## Conversation History Strategy (v1)

Three-layer model:

1. Raw session logs in Postgres (operational history)
2. Episodic summaries
3. Promoted facts/learnings (durable memory)

Only promoted facts/learnings become active long-term knowledge.

## Retrieval Contract (v1)

1. Mandatory domain filter first.
2. Intent/profile-based retrieval selection.
3. Per-profile allowed knowledge types + per-type `top_k`.
4. Hybrid ranking: semantic + authority + recency.
5. Confidence threshold gating before final context assembly.

## Context Quota (v1)

Dynamic by retrieval profile, with starting caps:

- Domain knowledge: 40-60%
- Case history/episodes: 20-30%
- Live tool evidence: 20-40%

## What Stays in Prompt (for now)

Keep in prompt files:

- role/persona
- output style constraints
- safety/policy instructions
- tool-call behavior rules

Move out of prompt files:

- state tables
- decision trees
- failure patterns
- evidence mappings
- workflow reference knowledge
