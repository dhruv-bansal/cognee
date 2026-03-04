# 07 - Embedding Model Guide (Use Cases + Cost Intuition)

## Why This Matters

Embeddings are a major cost driver in `cognify` because indexed data points are embedded for retrieval.

## Cost Snapshot Date

Pricing changes often. The numbers below are a snapshot as of **March 2, 2026** from provider pricing pages.

## Quick Model Table

| Model | Provider | Price Signal | Good For | Tradeoff |
|---|---|---|---|---|
| `text-embedding-3-small` | OpenAI | Low (about $0.02 / 1M input tokens) | High-volume ingestion, cost-sensitive workloads | Lower quality than large model on hard semantic matching |
| `text-embedding-3-large` | OpenAI | Medium (about $0.13 / 1M input tokens) | Better semantic recall/precision, harder enterprise queries | Higher cost than small model |
| `text-embedding-ada-002` | OpenAI | Medium (about $0.10 / 1M input tokens) | Legacy compatibility | Usually not the best price/quality now |
| `gemini-embedding-001` (standard) | Google | Medium-High (about $0.15 / 1M input tokens) | Google stack alignment, strong multilingual scenarios | Higher than cheapest OpenAI option |
| `gemini-embedding-001` (batch) | Google | Medium (about $0.075 / 1M input tokens) | Bulk offline embedding jobs | Batch workflow complexity |
| Local embedding model (for example via Ollama/FastEmbed) | Self-hosted | API cost near zero, infra cost applies | Data residency, predictable cost at scale | Ops complexity, hardware + latency tuning |

## Use-Case Recommendations

Use this starting logic:

1. Massive corpus + tight budget:
   - Start with `text-embedding-3-small` or local embeddings.
2. Complex policy/process reasoning with subtle terminology:
   - Start with `text-embedding-3-large`.
3. Very large nightly batch pipelines:
   - Prefer batch-priced options where available.
4. Strict privacy/on-prem requirement:
   - Use local embeddings and budget for infra.

## Simple Cost Intuition Example

If you embed 10M tokens:

- OpenAI `3-small`: about $0.20
- OpenAI `3-large`: about $1.30
- Gemini standard: about $1.50
- Gemini batch: about $0.75

This is only embedding cost, not LLM extraction/summarization cost.

## Practical Selection Process

1. Pick a baseline embedding model.
2. Run retrieval evaluation on representative queries.
3. Measure answer quality and miss rate.
4. Upgrade model only if benchmark results justify extra cost.

## Notes

- In Cognee, embedding provider/model is controlled via env config (`EMBEDDING_PROVIDER`, `EMBEDDING_MODEL`).
- Always re-check live pricing before committing to production budgets.

## Pricing Sources

- OpenAI API Pricing: https://openai.com/api/pricing/
- Google Gemini API Pricing: https://ai.google.dev/gemini-api/docs/pricing
