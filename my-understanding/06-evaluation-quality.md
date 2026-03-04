# 06 - Evaluation Quality (What "Insufficient" Means)

## What Is Evaluation Quality Here?

In this context, evaluation quality means:

- how good your `cognify`-built memory is for your real business questions.

It is not just "did pipeline run". It is "did memory help answer correctly and consistently".

## What "Insufficient Evaluation Quality" Means

When I said "upgrade model if evaluation quality is insufficient", I mean:

- the current cheaper setup fails your acceptance thresholds.

Typical failure signs:

- Missing key entities or relationships.
- Wrong relationship direction or weak relation names.
- Duplicate/conflicting entities.
- Poor answers on critical business queries even after retrieval.

## How It Is Used for Decision-Making

You use evaluation results to decide:

1. Keep cheaper model (if quality is acceptable).
2. Improve prompt/ontology/schema first.
3. Move to a stronger (more expensive) model only if needed.

## Minimal Evaluation Framework

Build a small benchmark set:

- 20-50 representative business queries.
- include easy, medium, hard, and edge-case queries.

Score each run on:

- Retrieval usefulness (context quality).
- Relationship correctness.
- Answer correctness.
- Coverage of policy/exception logic.

Use pass criteria, for example:

- Critical-query accuracy >= 90%.
- No severe factual errors on compliance-sensitive questions.
- Relationship extraction error rate below your defined threshold.

## Practical Evaluation Loop

1. Run `add` + `cognify` with cheaper model.
2. Evaluate on benchmark queries.
3. Fix prompt/schema/ontology issues.
4. Re-run evaluation.
5. If still below threshold, test stronger model.
6. Compare quality gain vs cost increase.

## Rule of Thumb

Model upgrade is the last lever, not first.

Usually improve in this order:

1. Better data curation.
2. Better extraction prompt.
3. Ontology/schema constraints.
4. Stronger extraction model.
