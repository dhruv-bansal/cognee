# 04 - Google ADK + Cognee Integration (Starter)

## Role Split

- Google ADK: agent orchestration, tool routing, response flow.
- Cognee: long-term reasoning memory (graph + vectors).

## Basic Runtime Pattern

1. User asks question in ADK agent.
2. Agent calls a memory tool backed by `cognee.search(...)`.
3. Agent uses returned memory context in final answer.
4. On important outcomes, write new knowledge with `cognee.add(...)`.
5. Run `cognify` asynchronously in background batches.

## Suggested Tool Surface for ADK

- `memory_search(query, scope, mode)`
- `memory_write(text, dataset, node_set)`
- `memory_refresh(dataset)` (runs cognify)
- `memory_temporal_search(query, dataset)`

## Search Mode Defaults

- General reasoning: `GRAPH_COMPLETION`
- Raw evidence: `CHUNKS`
- Time-based reasoning: `TEMPORAL`
- Rule extraction use cases: `CODING_RULES` pattern as reference, but customize for your domain

## Guardrails

- Keep transactional decisions validated against source-of-truth systems.
- Treat memory retrieval as context, not final authority.
- Log which memory snippets influenced answers.

## First Iteration Checklist

- Define 5 to 10 high-value business queries.
- Ingest only core docs first.
- Measure answer usefulness and failure patterns.
- Add structured schema only where failures repeat.
