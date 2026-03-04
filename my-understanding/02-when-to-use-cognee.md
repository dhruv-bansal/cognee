# 02 - When To Use Cognee

## Use Cognee When

- You need answers that depend on relationships across documents.
- Your domain has policies, exceptions, and historical decisions.
- You want memory that keeps improving instead of static retrieval.
- You need temporal queries (before/after/between events).

## Avoid or Limit Cognee When

- You only need simple FAQ retrieval from small static docs.
- You need strict transactional correctness as primary concern.
- You need deterministic rule execution with no LLM extraction risk.

## Decision Matrix

| Need | Best Fit |
|---|---|
| Exact transactional state | SQL/workflow engine |
| Fast semantic lookup | Vector DB / RAG |
| Relationship reasoning + memory evolution | Cognee |
| Compliance-grade deterministic rules | Rule engine |

## Recommended Production Pattern

- Source of truth: workflow/transaction system.
- Reasoning memory: cognee.
- Fast fallback retrieval: vector-only path.
