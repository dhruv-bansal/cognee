# 00 - Overview and Scope

## What Was Reviewed

Only these code locations were read:

- `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/platform`
- `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/agents/onebb-backend/agents`
- `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/evals`

No files were changed in those locations.

## Intent of This Documentation

- Understand current implementation approach before redesign.
- Capture what agents exist now and how they collaborate.
- Capture where domain knowledge currently lives.
- Capture what is already evaluated and what is not.

## Current Architecture at a Glance

```text
Client/API -> Orchestrator
             -> QuerySense gate
             -> Planner (tool-driven routing + execution plan write)
             -> Executor (reads execution plan + dispatches domain agents)
             -> Domain Agents (ProvisioningManager, WifiMeshAgent, others via config)

Shared runtime services:
- Agent Registry (discovery, heartbeat)
- MCP toolsets (external systems)
- Session DB (execution plan + resumability state)
- Prompt Hub (instruction files)
- Model Provider (Azure/OpenAI via LiteLlm)
```

## Key Understanding

1. This is already a multi-agent orchestration system, not a single-agent app.
2. Planner and Executor are the core service agents.
3. Provisioning Manager and Wifi Mesh are implemented as domain agents.
4. Knowledge is largely prompt-centric today, not managed as separate dynamic memory corpus.
5. Evals focus mainly on Planner/Executor orchestration correctness.

## Notes About Repository State

- There are local/uncommitted changes in `platform` and `agents` repos.
- This understanding emphasizes stable runtime flow from core files and may skip obviously local or inconsistent artifacts.
