# 01 - What Is Cognee

## One-Line Definition

`cognee` is a knowledge engine that builds graph + vector memory from raw data so agents can retrieve facts and relationships, not just similar text chunks.

## Core Pipeline

1. `add(...)` ingests data (text/files/urls) into datasets.
2. `cognify(...)` extracts entities, relations, summaries, and stores them in memory.
3. `search(...)` queries memory with multiple retrieval modes.
4. `memify(...)` enriches existing memory with additional tasks.

## Why It Matters for Agents

- Better multi-hop reasoning than plain vector-only retrieval.
- Persistent memory that can evolve over time.
- Supports domain slicing via dataset and node-set grouping.

## Minimal Mental Model

- Vector side: semantic similarity and chunk retrieval.
- Graph side: explicit entities and relationships.
- Agent side: asks questions against this memory before responding.

## Architecture Clarification

Cognee is primarily an application/knowledge layer that orchestrates memory workflows on top of storage engines.

In practice, it uses:

- relational DB for metadata and system state
- vector DB for embeddings and similarity retrieval
- graph DB for entities and relationships

So Cognee is not "just a database", and also not "just a stateless SDK". It is a memory engine layer plus APIs/pipelines.

## Deployment Patterns

### Pattern A: Embedded (POC / small apps)

- Cognee runs inside your Python app.
- Default local storages are file-based (`SQLite`, `LanceDB`, `Kuzu`).
- Fastest way to start.

### Pattern B: Independent service (production)

- Deploy Cognee backend separately (container/Kubernetes/VM).
- Connect it to managed/scalable databases (for example Postgres/pgvector, Neo4j, etc.).
- Agent apps call Cognee APIs/tools as an external memory service.

This pattern is closer to "like Postgres on cloud", but technically Cognee is the memory service layer, not the raw DB engine itself.

## Should You Use Cognee?

Use Cognee when you need:

- relationship-aware memory
- cross-document reasoning
- long-term evolving agent memory

If you only need basic FAQ lookup, a simpler vector-only setup may be enough.
