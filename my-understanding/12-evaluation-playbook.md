# 12 - Evaluation Playbook

## Objective

Evaluate whether your Cognee memory is good enough for real business use cases, before and after agent integration.

## Core Principle

Do evaluation in 3 layers:

1. Retrieval quality (no agent)
2. Answer quality (retrieval + answer generation)
3. End-to-end agent quality (ADK/production flow)

Do not jump straight to layer 3.

## Layer 1: Retrieval Quality (First Gate)

### What to test

- Can Cognee retrieve the right evidence for each business question?
- Are key entities and relationships present and correct?

### How to run

- Use `cognee.search(...)` directly.
- Test relevant modes:
  - `GRAPH_COMPLETION`
  - `CHUNKS`
  - `TEMPORAL` (if timeline questions exist)
  - `TRIPLET_COMPLETION` (if relationship-heavy questions exist)

### Metrics

- `hit@k`: expected evidence appears in top-k results.
- `entity_coverage`: expected entities found.
- `relation_coverage`: expected relationships found.
- `relation_direction_error_rate`: wrong edge direction rate.
- `duplication_rate`: duplicate/conflicting entity rate.

## Layer 2: Answer Quality

### What to test

- Is the final answer correct, complete, and grounded in retrieved context?

### Metrics

- `answer_correctness` (0/1)
- `answer_completeness` (0/1 or 0-2)
- `groundedness` (0/1): answer supported by retrieved context
- `critical_error` (0/1): unacceptable mistake on critical questions

## Layer 3: End-to-End Agent Quality

### What to test

- Can the full agent solve tasks reliably with Cognee memory?

### Metrics

- `task_success_rate`
- `tool_call_reliability`
- `latency_p95`
- `cost_per_task`
- `followup_consistency`

## Benchmark Set Design

Create 30-100 benchmark questions across categories:

- factual lookup
- relationship reasoning ("why/how related")
- policy + exception
- temporal queries ("before/after/between")
- adversarial/ambiguous queries

Weight critical business questions higher.

## Benchmark Row Template

Use this row shape in CSV/JSON:

| Field | Description |
|---|---|
| `id` | Stable test case id |
| `question` | User question |
| `query_mode` | SearchType being tested |
| `dataset_scope` | Dataset(s)/node_set scope |
| `expected_entities` | Must-have entities |
| `expected_relationships` | Must-have relations |
| `expected_time_constraints` | Time window if relevant |
| `criticality` | `high`/`medium`/`low` |
| `pass_rule` | Exact pass condition |

## Scoring Rubric (Simple)

For each test case:

- Retrieval pass:
  - 1 if all required evidence is present in top-k
  - 0 otherwise
- Answer pass:
  - 1 if correct and grounded
  - 0 otherwise
- Critical fail:
  - 1 if severe business/compliance error
  - 0 otherwise

## Example Acceptance Thresholds

Adjust these to your domain risk:

- Retrieval `hit@10` >= 85%
- Critical-case retrieval >= 95%
- Answer correctness >= 90%
- Critical error rate <= 1%

For compliance-heavy domains, use stricter thresholds.

## Experiment Matrix (What to Compare)

Evaluate multiple configurations:

1. baseline model + baseline embedding
2. improved prompt
3. ontology enabled
4. stronger LLM
5. stronger embedding model
6. triplet embedding enabled
7. temporal mode enabled (if needed)

Compare quality gain vs latency/cost increase.

## Failure Analysis Checklist

When a test fails, classify root cause:

1. ingestion issue (missing source data)
2. extraction issue (wrong/missing entities/relations)
3. retrieval issue (right memory exists but not retrieved)
4. synthesis issue (LLM answer poor despite good context)
5. routing issue (wrong search mode selected)

Fix in this order:

1. data coverage
2. extraction prompt/schema/ontology
3. retrieval mode/routing/top_k
4. model upgrade

## Practical Workflow

1. Build benchmark.
2. Run Layer 1 (retrieval only).
3. Fix major retrieval defects.
4. Run Layer 2 (answers).
5. Run Layer 3 (full agent).
6. Freeze baseline config.
7. Re-run benchmark on every major memory/model change.

## Minimal Starting Set

If you want to start fast, begin with:

- 10 high-criticality questions
- 10 relationship-heavy questions
- 10 temporal or exception questions

Then expand after first iteration.
