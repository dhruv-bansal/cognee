# 08 - Observed Gaps and Risks

This section captures code-level observations that may matter during architecture evolution.

## 1) Inventory and Config Drift

- Top-level agents `pyproject.toml` still references `classification-agent` and `diagnostic-agent`, while current folders are planner/orchestrator/executor/provisioning/wifi/query-sense.
- Multiple agent READMEs are empty, reducing onboarding clarity.

## 2) Runtime Dependency Fragility

- Executor dispatch depends on `REMOTE_AGENT_CONFIG` env JSON; invalid/missing JSON silently gives empty map, causing runtime invalid-agent errors.
- Planner->Executor contract depends on shared custom session DB state; this is a hard coupling point.

## 3) Knowledge Management Is Prompt-Heavy

- Provisioning domain has large instruction markdowns.
- Planner and Wifi have large in-code instruction blocks.
- Knowledge is distributed across multiple prompt surfaces with limited central governance.

## 4) Discovery and Tagging Assumptions

- `discover_registered_agents` skips any agent where tags include `Service`.
- Correct routing depends on consistent tag assignment in registration.

## 5) Eval-Environment Alignment Gaps

- Evals reference `NetworkAgent` and `PlayerAgent`, which are not present in this agent repo; they may exist externally or in another environment.
- This can create false negatives if runtime inventory differs from dataset assumptions.

## 6) Operational Control Points

- Registry is in-memory and marks offline by heartbeat staleness; no persistent registry state.
- HIL plugin enablement is env-driven and should be checked carefully per environment.
- Compaction and resumability are active; long-running sessions rely on robust session DB health.

## 7) Domain-Agent Consistency

- Provisioning has two-stage validate/challenge pipeline.
- Wifi mesh is single-agent only.
- Design conventions for domain-agent rigor are not yet standardized across agents.

## 8) Prompt and Tool Evolution Risk

- Prompt Hub loader loads all `*_Instruction.md` at module import and prints debug info.
- Large prompts plus frequent changes can impact deterministic behavior unless backed by strong regression evals.

## Practical Implication

Before scaling to many domain agents, standardization is needed in:

- agent packaging and naming conventions
- required docs and env schemas
- prompt governance and change testing
- evaluator coverage for domain-quality and tool-groundedness
