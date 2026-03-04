# 09 - Temporal Mode

## What It Is

Temporal mode is a `cognify` path optimized for time-aware memory and queries.

You enable it with:

- `temporal_cognify=True`

and query with:

- `SearchType.TEMPORAL`

## What It Does Differently

Default `cognify` focuses on general entity-relationship extraction.

Temporal mode adds time-specific extraction:

1. Extract events and timestamps from chunks.
2. Convert events into event datapoints.
3. Enrich events with related entities.
4. Store and index for temporal retrieval.

## Query Behavior

Temporal retrieval typically works like this:

1. Extract time interval from user query (for example "before 2020", "between 2021 and 2023").
2. Fetch events matching that interval from graph storage.
3. Rank/select relevant events with vector similarity.
4. If no clear time interval is found, fallback to relationship-based retrieval.

## Example Query Types

- "What happened before 2018?"
- "Which milestones occurred between 2020 and 2022?"
- "What changed after policy X was introduced?"

## When To Use

Use temporal mode when your business process depends on:

- sequences of events
- before/after logic
- trend analysis over time
- audit/history reasoning

If your use case is mostly static factual lookup, default mode is usually enough.

## Tradeoffs

- Additional extraction steps.
- Potentially higher ingestion cost.
- More complexity in evaluation and prompt design.

## Where It Appears in Code

- Temporal task pipeline in `cognee/api/v1/cognify/cognify.py` (`get_temporal_tasks`)
- Event extraction task: `cognee/tasks/temporal_graph/extract_events_and_entities.py`
- Temporal retriever: `cognee/modules/retrieval/temporal_retriever.py`
