# 10 - Agentic Use Cases and Mode Mapping

## What Cognee Is Intended For

Cognee is most useful for agents that need:

- persistent memory over time
- relationship-aware reasoning (not just similar text retrieval)
- multi-source knowledge (docs, conversations, logs, policies)
- evolving knowledge with incremental updates

It is less suitable as a replacement for strict transactional systems (SQL/workflow engines).

## Strong Agentic Use Cases

1. Procurement and vendor decision assistants
2. Policy and compliance copilots
3. Incident response and postmortem assistants
4. Customer support agents with long-term case memory
5. Internal coding assistants (team rules, architecture memory)
6. Research analysts and due-diligence agents
7. Knowledge-heavy operations assistants (legal, finance ops, HR ops)
8. Enterprise search copilots with cross-document reasoning

## Processing Modes (Cognify)

| Processing Mode | What It Optimizes | Recommended Use Case |
|---|---|---|
| Default `cognify` | General entity + relation memory | Most business knowledge assistants |
| `temporal_cognify=True` | Event/time extraction and timeline queries | Audit trails, incident timelines, milestone tracking |

## Search Modes (SearchType) and Recommended Use Cases

| Search Mode | Best For | Recommended Agentic Use Case |
|---|---|---|
| `GRAPH_COMPLETION` | Graph-aware Q&A (default) | General business assistant, policy reasoning |
| `RAG_COMPLETION` | Chunk-based completion without graph traversal | Fast factual answer assistant |
| `CHUNKS` | Raw evidence retrieval | Citation/evidence view in review workflows |
| `CHUNKS_LEXICAL` | Lexical/token overlap matching | Exact-term compliance checks, terminology-sensitive domains |
| `SUMMARIES` | Precomputed summaries | Executive briefing agent, quick overview mode |
| `GRAPH_SUMMARY_COMPLETION` | Summarized graph context + answer | Report-generation assistants |
| `TRIPLET_COMPLETION` | Relationship-centric retrieval | Dependency/rule-relationship questions |
| `TEMPORAL` | Time-aware retrieval | Timeline and before/after analysis agents |
| `CODING_RULES` | Specialized coding-rule retrieval | Engineering standards and code policy assistants |
| `GRAPH_COMPLETION_COT` | Iterative reasoning over graph context | Hard, multi-step analytical queries |
| `GRAPH_COMPLETION_CONTEXT_EXTENSION` | Broader iterative context expansion | Ambiguous questions needing wider context |
| `CYPHER` | Direct graph query workflows | Power-user analytical tools, debugging graph state |
| `NATURAL_LANGUAGE` | NL-to-graph querying path | Analyst assistants preferring NL graph queries |
| `FEELING_LUCKY` | Auto-select mode by query | Early prototyping and UX simplification |

## Suggested Defaults for a New Agent

1. Start with `GRAPH_COMPLETION`.
2. Add `CHUNKS` for evidence transparency.
3. Add `TEMPORAL` only if timeline questions matter.
4. Add `TRIPLET_COMPLETION` when relationship queries are common.
5. Keep advanced modes (`CYPHER`, `GRAPH_COMPLETION_COT`) for expert or internal flows.

## Practical Router Strategy

Use simple intent routing:

- If query asks "before/after/between" -> `TEMPORAL`
- If query asks "show source / quote exact text" -> `CHUNKS`
- If query asks "how are X and Y related" -> `TRIPLET_COMPLETION` or `GRAPH_COMPLETION`
- Otherwise default -> `GRAPH_COMPLETION`
