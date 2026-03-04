# 05 - Cognify Function

## Purpose

`cognify(...)` converts ingested raw data into usable memory by building graph and vector representations.

In simple terms:

- `add(...)` stores data.
- `cognify(...)` understands and structures data.
- `search(...)` retrieves from that structured memory.

## Where It Lives

- API entrypoint: `cognee/api/v1/cognify/cognify.py`
- Graph extraction task: `cognee/tasks/graph/extract_graph_from_data.py`
- LLM extraction call: `cognee/infrastructure/llm/extraction/knowledge_graph/extract_content_graph.py`

## Pipeline Steps

Default `cognify` pipeline runs these tasks in order:

1. `classify_documents`
2. `extract_chunks_from_documents`
3. `extract_graph_from_data`
4. `summarize_text`
5. `add_data_points`

Effect:

- Documents become chunks.
- Chunks become nodes + relationships.
- Results are persisted and indexed for retrieval.

## How Relationships Are Found

Relationship extraction is mainly LLM-driven, then validated and normalized.

1. For each chunk, Cognee prompts the LLM with graph-extraction instructions.
2. The LLM returns structured output (`KnowledgeGraph`) with:
   - `nodes`
   - `edges` (`source_node_id`, `target_node_id`, `relationship_name`)
3. Cognee removes invalid edges (missing source/target nodes).
4. Cognee expands and canonicalizes nodes/edges, optionally aligning with ontology.
5. Cognee checks existing edges to reduce duplicates.
6. Cognee stores nodes/edges in graph DB and indexes them for search.

## Most Important Parameters

- `datasets`: limit processing scope.
- `graph_model`: custom schema for domain-specific extraction.
- `custom_prompt`: steer extraction behavior and relation naming.
- `config` (ontology): constrain vocabulary/entity mapping.
- `temporal_cognify=True`: build time-aware memory.
- `chunk_size`, `chunks_per_batch`: quality vs throughput tradeoff.
- `run_in_background=True`: async processing for larger corpora.
- `incremental_loading=True`: process only new/changed items.

## What Kind of LLM Works Best for Cognify

For `cognify`, prioritize these capabilities over pure chat quality:

- Strong structured-output reliability (must return valid schema consistently).
- Good entity/relationship extraction from long, messy text.
- Stable behavior at low temperature.
- Reasonable price per token for batch processing.

Practical model strategy:

- Development and prompt tuning:
  - Use a cheaper/faster model first.
- Production extraction:
  - Use a mid-tier model with reliable structured output.
- High-risk domains (legal/compliance-heavy):
  - Consider a stronger model for extraction quality, then evaluate cost impact.

Provider support in Cognee includes:

- `openai`, `anthropic`, `gemini`, `mistral`, `bedrock`, `ollama`, `llama_cpp`, `custom`.

Important:

- `cognify` also uses embeddings, so embedding model cost matters separately from LLM extraction cost.

## Cost Reality: What Is Expensive vs Cheap

Your concern is correct for large datasets, but one nuance matters:

- `classify_documents` in default `cognify` is extension/type mapping and is generally cheap.
- Biggest cost drivers are usually:
  - Graph extraction LLM calls per chunk (`extract_graph_from_data`)
  - Summarization LLM calls per chunk (`summarize_text`)
  - Embedding generation for indexed nodes/fields

So cost grows roughly with:

- number of chunks
- average chunk size
- number of extracted/indexed nodes
- embedding dimensions/model price

If `temporal_cognify=True`, extra extraction steps are added, so cost can increase.

## Cost Control Playbook

1. Start small by dataset:
   - Run `cognify` on one domain dataset at a time, not everything together.
2. Keep `incremental_loading=True`:
   - Avoid reprocessing unchanged data.
3. Reduce chunk explosion:
   - Use a larger `chunk_size` where quality remains acceptable.
4. Use a cheaper extraction model first:
   - Upgrade only if evaluation quality is insufficient.
5. Optimize embedding spend:
   - Use a cheaper embedding model when acceptable.
6. Avoid extra work unless needed:
   - Keep triplet embedding off unless required.
   - Use temporal mode only for truly time-based queries.
7. Customize pipeline if needed:
   - You can run a custom pipeline and skip tasks like summarization for cost-sensitive flows.
8. Gate ingestion quality:
   - Ingest only high-value docs first; avoid noisy low-value bulk dumps.

## Minimal Usage

```python
import cognee

await cognee.add(["Your business process text here"], dataset_name="procurement_core")
await cognee.cognify(datasets=["procurement_core"])
```

## Quality Checklist for Business Process Memory

- Are relationship names consistent and domain-meaningful?
- Are key entities missing or duplicated?
- Are policy and exception links captured?
- Are time-dependent events modeled when needed?
- Does query output answer real stakeholder questions?

## Common Pitfalls

- Using only default extraction for a complex domain for too long.
- No ontology/prompt constraints for high-precision use cases.
- Treating memory output as system-of-record truth.
- Mixing unrelated domains into one dataset without node-set boundaries.
- Running full re-cognify on all data after minor updates.
- Assuming classification is the main cost driver (usually it is not).

## Practical Rule

Start with default `cognify`, validate real queries, then harden with:

1. Custom prompt
2. Ontology
3. Custom `graph_model`
4. Post-enrichment (`memify`)

## Related Deep Dives

- Evaluation quality and acceptance thresholds: `06-evaluation-quality.md`
- Embedding model and cost intuition: `07-embedding-model-guide.md`
- Relationship-centric indexing with triplets: `08-triplet-embedding.md`
- Time-aware ingestion and search: `09-temporal-mode.md`
