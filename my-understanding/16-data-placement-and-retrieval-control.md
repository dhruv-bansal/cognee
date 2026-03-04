# 16 - Data Placement and Retrieval Control

## Why This Matters

If you put all data in one place, retrieval gets noisy and expensive.
If you split data by access pattern, Cognee can retrieve faster and more accurately.

## What Goes Where

| Layer | Put This Data Here | Why |
|---|---|---|
| Relational DB | Datasets, users, ACLs, ingestion status, file metadata, pipeline status | Transactional metadata and permissions |
| Vector DB | Embeddings for chunks, entity names, summaries, triplets, events | Fast semantic lookup |
| Graph DB | Entities, edges, temporal/event relationships | Multi-hop reasoning and relationship traversal |
| Object Storage | Raw files, large artifacts, originals | Cheap storage for large unstructured data |
| Observability Stack | Runtime logs, traces, metrics, usage/latency/error monitoring | Operations and debugging, not memory retrieval |

## How To Decide Data Placement

Use query intent:

1. If you ask "who/what is related to what?" -> graph.
2. If you ask "find similar text about X" -> vector.
3. If you need durable app metadata/ownership/permissions -> relational.
4. If data is large raw artifact (PDF/audio/image/log file) -> object storage.
5. If data is high-volume runtime signal (telemetry/log stream) -> observability system first.

## Example (Complex Business Process)

Input sources:

- SOP and policy docs
- ticket history
- incident timeline
- service telemetry

Placement:

- Raw SOP PDFs and exported tickets -> object storage.
- Chunk embeddings + summaries -> vector.
- Entities/relations like `Service -> depends_on -> DB`, `Incident -> impacted -> Region` -> graph.
- Dataset ownership, ACLs, ingestion states -> relational.
- Full raw telemetry stream -> observability platform (not fully ingested into Cognee memory).

## How Cognee Knows Where To Fetch From

Cognee routes retrieval by `SearchType` (retriever factory).  
Examples:

- `CHUNKS` / `RAG_COMPLETION`: vector (`DocumentChunk_text`)
- `TRIPLET_COMPLETION`: vector (`Triplet_text`)
- `GRAPH_COMPLETION`: vector pre-retrieval across collections + graph projection/ranking
- `TEMPORAL`: time extraction + graph event filtering + vector scoring (`Event_name`)
- `GRAPH_SUMMARY_COMPLETION`: same graph retrieval, then summary compression
- `FEELING_LUCKY`: LLM picks search type; fallback is `RAG_COMPLETION` if selection fails

So retrieval source is not random; it is determined by query type and retriever logic.

## How Much Data Is Fetched

Primary controls:

- `top_k`: final number of returned items/triplets/chunks
- `wide_search_top_k`: broader candidate pull before graph ranking
- dataset filters (`datasets` / `dataset_ids`)
- node filters (`node_name`, `node_type`)
- retriever mode (`GRAPH_SUMMARY_COMPLETION` vs `GRAPH_COMPLETION`)

Important: Cognee does not enforce a strict token budget in retrieval context assembly by default. You control breadth with the knobs above.

## What If Context Is Larger Than LLM Window

Use this order:

1. Reduce `top_k`.
2. Reduce `wide_search_top_k`.
3. Scope by dataset and node filters.
4. Switch to `GRAPH_SUMMARY_COMPLETION`.
5. Use `only_context=True` to inspect context size before completion.
6. Do staged retrieval (coarse -> refine -> answer), not one large fetch.

## Should You Put Streaming Logs/Telemetry Into Cognee?

Not as raw full stream.

Recommended pattern:

1. Keep raw logs/metrics/traces in observability stack.
2. Derive higher-value memory facts (incident summaries, recurring failure patterns, postmortem conclusions, SLO breach events).
3. Ingest only those curated/aggregated facts into Cognee on a schedule or trigger.

Reason: raw streams are high-volume, low signal, and expensive to embed continuously.

## Practical Ingestion Policy (Cost + Quality)

Use a two-lane policy:

- Lane A (high-value memory): policies, runbooks, architecture, incident summaries -> ingest to Cognee.
- Lane B (high-volume ops data): raw logs/traces/metrics -> keep in observability; periodically summarize into Lane A.

This keeps memory quality high and ingestion cost controlled.

## Other Components In A Production Setup

- Ingestion workers (batch + event-driven)
- ETL/normalization layer for documents and events
- Access control and tenant isolation
- Session/cache layer for conversational memory
- Evaluation pipeline (retrieval precision/recall, answer groundedness)
- Observability and cost dashboards

## Repo References

- `cognee/modules/search/methods/get_search_type_retriever_instance.py`
- `cognee/modules/search/methods/get_retriever_output.py`
- `cognee/modules/retrieval/chunks_retriever.py`
- `cognee/modules/retrieval/completion_retriever.py`
- `cognee/modules/retrieval/graph_completion_retriever.py`
- `cognee/modules/retrieval/graph_summary_completion_retriever.py`
- `cognee/modules/retrieval/temporal_retriever.py`
- `cognee/modules/retrieval/utils/brute_force_triplet_search.py`
- `cognee/modules/retrieval/utils/node_edge_vector_search.py`
- `cognee/modules/data/models/Data.py`
- `cognee/modules/data/models/Dataset.py`
- `cognee/infrastructure/databases/relational/config.py`
- `cognee/infrastructure/databases/vector/config.py`
- `cognee/infrastructure/databases/graph/config.py`
- `cognee/infrastructure/files/storage/get_file_storage.py`
- `cognee/modules/observability/get_observe.py`
