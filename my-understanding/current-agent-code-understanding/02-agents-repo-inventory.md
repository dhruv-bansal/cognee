# 02 - Agents Repo Inventory

Repo reviewed: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/agents/onebb-backend/agents`

## Agent Folders Present

- `orchestrator-agent`
- `planner-agent`
- `executor-agent`
- `query-sense-agent`
- `provisioning-manager-agent` (domain agent)
- `wifi-mesh-agent` (domain agent)

## Role Mapping

Service/control agents:

- Orchestrator Agent: entrypoint flow control (QuerySense then Planner+Executor)
- Planner Agent: routing + execution-plan creation tool usage
- Executor Agent: execution-plan dispatch and aggregation
- Query Sense Agent: front filter, decides if deeper analysis is required

Domain agents:

- ProvisioningManager Agent: provisioning diagnostics and root cause support
- WifiMesh Agent: wifi configuration and mesh troubleshooting support

## Core Runtime Characteristics

Common patterns across most agents:

- Google ADK agents served via A2A wrappers.
- Registration heartbeat to Agent Registry.
- Tracing + logging decorators.
- Session DB support via `ADK_SESSION_DB_URL`.
- Environment-driven configuration using pydantic settings.

## Notable Dependency Patterns

- Planner uses `dt-mcp-tool` custom tools (`discover_registered_agents`, `set_execution_plan`).
- Executor depends heavily on session custom state + `REMOTE_AGENT_CONFIG`.
- Provisioning and Wifi domain agents use MCP toolsets from local `mcp-config.json`.
- Provisioning adds memory search + reflection callback (`dt-agent-memory`).

## Agent-Specific Notes

### Orchestrator Agent

- `README.md` currently empty.
- Defines explicit custom session creation API route under `script.py`.
- Uses local QuerySense LlmAgent first, then SequentialAgent of Planner+Executor.

### Planner Agent

- `README.md` currently empty.
- Contains very strict instruction file in code (`instructions.py`) enforcing tool usage and routing discipline.
- Exposed tags: `Home`, `Service`.

### Executor Agent

- `README.md` currently empty.
- `ExecutorWorkflow` executes plan sequentially and supports resume from last agent state.
- Optional multi-agent response aggregation via LLM summarization.

### Query Sense Agent

- Has readable `README.md` and explicit behavior expectations.
- Uses prompt-hub instruction by `AGENT_NAME.lower()`.

### Provisioning Manager Agent (Domain)

- `README.md` currently empty.
- Sequential agent with `Investigator` and `Challenger` sub-agents.
- Uses both MCP toolsets and internal Mongo/log helper tools.
- Uses prompt-hub instructions for domain-specific reasoning.

### Wifi Mesh Agent (Domain)

- `README.md` currently empty.
- Single LlmAgent using MCP streamable toolsets.
- Domain behavior is encoded in local `instructions.py`.

## Operational Configuration Surfaces

- `.env.sample` exists in each agent folder.
- `mcp-config.json` exists for domain agents (Provisioning/Wifi).
- `config.yaml` includes vector/log analysis related settings for domain flows.

## Inventory Caveats

- Top-level `agents/pyproject.toml` references `classification-agent` and `diagnostic-agent` paths not currently present as folders.
- Executor `.env.sample` contains legacy URL variables (`PROVISIONING_AGENT_URL`) while runtime dispatch uses `REMOTE_AGENT_CONFIG`.

These caveats are likely transition artifacts and should be validated before hardening CI/runtime automation.
