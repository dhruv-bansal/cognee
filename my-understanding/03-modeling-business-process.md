# 03 - Modeling a Complex Business Process in Cognee

## Example Domain

Enterprise procurement with approvals, policy checks, exceptions, and vendor performance.

## Start Simple (Phase 1)

Ingest these data sources first:

- SOP/process docs
- Policy docs
- Incident and exception logs
- Meeting notes
- Historical decisions

Suggested ingestion grouping:

- `dataset_name="procurement_core"`
- `node_set=["policies"]`
- `node_set=["history"]`
- `node_set=["vendors"]`
- `node_set=["exceptions"]`

## Add Structure (Phase 2)

Define stable entities:

- `Process`
- `Stage`
- `Role`
- `PolicyRule`
- `Vendor`
- `ExceptionCase`
- `Event`

Define key relationships:

- `Stage requires PolicyRule`
- `Role approves Stage`
- `ExceptionCase overrides PolicyRule`
- `Vendor violated SLA`
- `Event occurred_in Stage`

## Modeling Heuristics

- Start with fewer entity types; add only when queries fail.
- Keep relationship names domain-readable.
- Use timestamps for major events.
- Separate governance/policy memory from execution/history memory.

## Query Targets You Should Validate

- Why was request X rejected?
- Which rule blocked approval?
- What exceptions were used before?
- Which vendors repeatedly violate SLA?
- What changed in the process after date Y?

## Practical Build Sequence

1. Ingest text and run `cognify`.
2. Evaluate real queries from users/stakeholders.
3. Add custom schema (`DataPoint`) for recurring entity patterns.
4. Add ontology/custom prompt if extraction quality is inconsistent.
5. Add `memify` enrichment for domain-specific derived knowledge.
