# 08 - Triplet Embedding

## What It Is

Triplet embedding means embedding relationship triples in the form:

- `(source_node) -[relationship]-> (target_node)`

instead of embedding only node/chunk text.

## How Cognee Uses It

When triplet embedding is enabled, Cognee creates `Triplet` datapoints from graph edges and embeds them for retrieval.

Internally:

- Edges are converted to text like `source -› relationship -› target`.
- Edges are converted to text like `source -> relationship -> target`.
- These triplets are indexed in vector storage (for example `Triplet_text` collection).

## Why It Can Help

- Better retrieval of relationship-centric queries.
- Useful when meaning is in the connection, not only in entity names.
- Can improve graph-aware completion quality for multi-hop reasoning.

## Tradeoffs

- More embeddings generated.
- More vector storage.
- Higher ingestion cost and longer processing time.

## When To Use

Use triplet embedding when:

- Your key queries ask about relationships ("who depends on what", "what causes what").
- Entity-only/chunk-only retrieval misses important links.

Skip or delay triplet embedding when:

- You are still validating basic memory quality.
- You are cost-constrained and relation retrieval is not yet critical.

## Where It Appears in Code

- Triplet creation and indexing: `cognee/tasks/storage/add_data_points.py`
- Config flag in cognify config: `cognee/modules/cognify/config.py` (`triplet_embedding`)
- Retrieval path: `TRIPLET_COMPLETION` and triplet retriever modules

## Practical Rollout Strategy

1. Start without triplet embedding.
2. Benchmark relationship-heavy queries.
3. Enable triplets only if measurable quality improves.
