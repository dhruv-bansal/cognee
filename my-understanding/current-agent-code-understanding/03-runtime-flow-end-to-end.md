# 03 - Runtime Flow End to End

This document captures how a user request moves through the current multi-agent system.

## High-Level Flow

```text
Client request
  -> Orchestrator session creation endpoint
  -> QuerySense decision
  -> Planner route + set execution plan
  -> Executor runs domain agents from execution plan
  -> Aggregated final response
```

## Step 1: Session Bootstrap (Orchestrator)

File: `orchestrator-agent/src/orchestrator_agent/script.py`

- Custom endpoint: `POST /home-ai/apps/{app_name}/users/{user_id}/sessions`
- Validates client headers (expects Magnus flow).
- Calls Magnus tenant API to resolve tenant context.
- Creates ADK session.
- Writes custom session state with tenant/environment.

Result: shared session context is created for downstream tools and routing.

## Step 2: Query Gate (QuerySense)

Files:

- `orchestrator-agent/src/orchestrator_agent/workflow.py`
- `orchestrator-agent/src/orchestrator_agent/query_sense_agent.py`
- `platform-ai-core/dt-prompt-hub/src/dt_prompt_hub/QuerySense_Instruction.md`

Behavior:

- QuerySense returns strict JSON:
  - `response`
  - `require_further_analysis`
  - `conversation_summary`
- If `require_further_analysis=false`, orchestrator returns response directly.
- If true, orchestrator rewrites session events with `conversation_summary` and enters workflow stage.

## Step 3: Planner (Routing + Plan Write)

Files:

- `planner-agent/src/planner_agent/agent.py`
- `planner-agent/src/planner_agent/instructions.py`
- `platform-ai-core/dt-mcp-tool/src/dt_mcp_tool/tools/discover_agents.py`
- `platform-ai-core/dt-mcp-tool/src/dt_mcp_tool/tools/set_execution_plan.py`

Behavior:

- Planner is tool-centric; uses:
  - `discover_registered_agents`
  - `set_execution_plan`
- Planner instruction enforces strict agent-name usage and mandatory plan-set on confirmation.
- `set_execution_plan` writes to `custom_states`:
  - `execution_plan`
  - reset `ExecutorAgent_agent_state`

Result: executor gets a structured plan in shared session state.

## Step 4: Executor (Dispatch + Aggregation)

File: `executor-agent/src/executor_agent/workflow.py`

Behavior:

- Reads `execution_plan` from custom session state.
- Loads remote agents from `REMOTE_AGENT_CONFIG` JSON env var.
- Dispatches sub-agents sequentially.
- Supports resumable flow via saved `ExecutorAgent_agent_state`.
- If multiple agents were run, fetches each final response from session and runs LLM aggregation prompt.

Error branches:

- Empty/malformed plan -> generic `[ERROR]` message.
- Unknown agent in plan -> invalid routing `[ERROR]` message.

## Step 5: Domain Agent Execution

Domain agents run via A2A and receive `agent_enhanced_query`.

- Provisioning Manager: Investigator -> Challenger pipeline, heavy MCP + domain tools + memory callback.
- Wifi Mesh: single LLM agent with MCP tools for wifi operations.

## Metadata and Context Propagation

- Remote A2A metadata provider passes `tenant`, `environment`, `authorization` when available.
- Session state plugin injects `a2a_metadata` into tool context state.
- Mongo-backed tools rely on `tenant` and `environment` values from state.

## Compaction and Resumability

Framework supports:

- resumable invocations
- conversation compaction with summarizer
- info event emission when compaction happens

This helps maintain long sessions while keeping token usage bounded.

## Current Architectural Shape

- Orchestrator manages lifecycle and branching.
- Planner decides and records what to execute.
- Executor performs deterministic sequence execution of selected agents.
- Domain agents hold domain-level reasoning and tool integrations.

This is a clean control-plane vs domain-plane split.
