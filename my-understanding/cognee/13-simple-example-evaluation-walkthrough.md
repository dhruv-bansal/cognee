# 13 - Simple Example Evaluation Walkthrough

## Goal

Run the evaluation playbook on one tiny example first, so the method is easy to understand.

Base example from repo:

- `examples/guides/search_basics_core.py`

## First-Time Setup (From This Repository)

### Prerequisites

- Python `3.10` to `3.13`
- `uv` installed
- OpenAI API key (or another configured provider)
- Optional for UI: Node.js + npm

### 1) Install dependencies

From repository root:

```bash
uv sync --dev --all-extras --reinstall
```

### 2) Create environment file

```bash
cp .env.template .env
```

Edit `.env` at minimum:

```env
LLM_API_KEY="your_key_here"
```

Defaults are already local-friendly:

- relational DB: SQLite
- vector DB: LanceDB
- graph DB: Kuzu

So no extra database setup is required for this POC.

## Step 0: Use This Tiny Dataset

This example adds only 3 short facts:

1. Alice moved to Paris in 2010 and works as software engineer.
2. Bob lives in New York and is a data scientist.
3. Alice and Bob met at a conference in 2015.

## Step 1: Run The Baseline Pipeline

1. Configure API key in `.env`.
2. Run:

```bash
uv run python examples/guides/search_basics_core.py
```

This gives your first baseline memory.

## Step 1.1: Visualize What Was Built

You have two simple options.

### Option A: Generate a graph HTML file

Run:

```bash
uv run python - <<'PY'
import asyncio
from pathlib import Path
from cognee.api.v1.visualize.visualize import visualize_graph

async def main():
    out = Path("my-understanding/.artifacts/simple-example-graph.html")
    out.parent.mkdir(parents=True, exist_ok=True)
    await visualize_graph(str(out))
    print(f"Graph written to: {out.resolve()}")

asyncio.run(main())
PY
```

This generates an HTML graph artifact at:

- `my-understanding/.artifacts/simple-example-graph.html`

Open the generated HTML in your browser to inspect nodes/edges visually.

### Option B: Open Cognee local UI

Run:

```bash
uv run cognee-cli -ui
```

Expected endpoints:

- UI: `http://localhost:3000`
- API (if started by UI mode): `http://localhost:8000`

Notes for first-time UI usage:

- It may download/setup frontend assets on first run.
- If ports are busy, stop conflicting processes or use different ports.

## Step 2: Start With Layer 1 (Retrieval Quality)

Use direct `cognee.search(...)` queries and check if expected evidence is retrieved.

### Tiny Benchmark Set (start with 6 questions)

| ID | Question | Expected Evidence |
|---|---|---|
| Q1 | Where does Alice live? | Alice -> Paris |
| Q2 | What is Alice's profession? | Alice -> software engineer |
| Q3 | Where does Bob live? | Bob -> New York |
| Q4 | What is Bob's profession? | Bob -> data scientist |
| Q5 | Did Alice and Bob ever meet? | Alice/Bob -> met |
| Q6 | When did they meet? | conference in 2015 |

### Scoring Rule (simple)

For each question:

- retrieval_pass = 1 if top-k result contains required evidence
- retrieval_pass = 0 otherwise

Start with `top_k=5` and compute:

- retrieval_accuracy = sum(retrieval_pass) / total_questions

Tip:

- Run each question first with `GRAPH_COMPLETION`.
- If an answer is vague, re-run with `CHUNKS` to inspect raw evidence.

## Step 3: Layer 2 (Answer Quality)

Now judge returned answers:

- answer_correctness (0/1)
- groundedness (0/1): answer supported by retrieved evidence

For first iteration, manual scoring is enough.

## Step 4: Interpret Results

- If retrieval is low:
  - inspect ingestion text quality
  - inspect query wording
  - try mode changes (`GRAPH_COMPLETION` vs `CHUNKS`)
- If retrieval is good but answers are weak:
  - improve prompt/system prompt
  - then test stronger model if needed

## Step 5: Expand Gradually

After this small set works:

1. Add 10-20 business-real questions.
2. Add relation-heavy "why/how related" questions.
3. Add temporal questions and test temporal mode.
4. Then test full agent workflow (Layer 3).

At that point, wire this same benchmark into your ADK agent flow for end-to-end checks.

## Minimal Pass Target For This Starter

Use these temporary targets:

- Retrieval accuracy >= 80% on this tiny set.
- Answer correctness >= 80%.
- Groundedness >= 90%.

These are starter thresholds only. Tighten later for production.

## Why This Helps

This method separates:

- memory quality problems
- retrieval/routing problems
- answer generation problems

So you can fix the right layer instead of guessing.
