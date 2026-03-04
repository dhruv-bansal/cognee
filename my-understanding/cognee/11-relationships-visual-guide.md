# 11 - Relationships Visual Guide

## Why This Feels Hard To Visualize

Vector retrieval and graph retrieval look similar from the outside (both return context), but they solve different problems.

- Vector: finds semantically similar text chunks.
- Graph: finds connected facts across chunks/entities.

## Relationship vs Non-Relationship Data

| Data Type | Has Relationship Structure? | Example |
|---|---|---|
| Policy + exceptions | Yes | `Policy A` overridden by `Exception B` |
| Process + owners + approvals | Yes | `Stage 3` approved by `Finance` |
| Incident + root cause + fix | Yes | `Deploy X` caused `Incident Y`; fixed by `Patch Z` |
| Timeline history | Yes | `Event B` happened after `Event A` |
| FAQ answers | Weak/Low | Independent Q/A pairs |
| Standalone product descriptions | Weak/Low | Each description is mostly self-contained |
| One-off notes | Weak/Low | No stable entities linked across docs |

## Visual Mental Model

### Vector-Only Memory

```text
Query -> find top similar chunks
```

Great for:

- "Find the paragraph about refund policy."

Weak for:

- "Why was vendor Z rejected despite low cost?"

### Graph + Vector Memory

```text
Query
  -> find relevant entities/chunks
  -> traverse links between entities
  -> gather connected evidence
```

Example:

```text
[Vendor Z] --offered_price--> [$120k]
[Policy: 2 approvals over $100k] --applies_to--> [Procurement]
[Manager Approval] --missing_for--> [Vendor Z bid]
[Decision: Rejected] --because_of--> [Missing Approval]
```

Now the agent can answer "why" instead of returning isolated snippets.

## What Improves in Practice

When relationships exist, Cognee can improve:

- multi-hop reasoning ("X because Y because Z")
- consistency across follow-up questions
- explainability (traceable linked context)
- recall of cross-document logic (policy + exceptions + history)

## When Cognee May Not Add Much

If your workload is mostly:

- single-doc lookup
- exact phrase retrieval
- independent FAQ responses

then vector-only RAG may be enough.

## Quick Test To Decide

Ask these:

1. Do answers depend on links between entities across documents?
2. Do users ask many "why/how related" questions?
3. Do timeline/order-of-events questions matter?

If mostly yes, relationship-aware memory is worth it.
