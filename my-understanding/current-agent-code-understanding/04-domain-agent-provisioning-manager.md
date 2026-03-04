# 04 - Domain Agent: Provisioning Manager

Folder: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/agents/onebb-backend/agents/provisioning-manager-agent`

## What This Agent Does

Provisioning Manager is a domain diagnosis agent for OneBroadband provisioning and CPE lifecycle issues.

It is implemented as a `SequentialAgent` with two sub-agents:

1. `ProvisioningManager_Investigator`
2. `ProvisioningManager_Challenger`

The intent is two-stage reasoning:

- Investigator gathers evidence and initial diagnosis.
- Challenger critiques and validates, then returns final answer.

## Implementation Highlights

File: `src/provisioning_manager_agent/agent.py`

- Agent is A2A-enabled and registered as domain-tagged (`Onebb`, `Domain`).
- Both sub-agents use:
  - memory search tool (`langmem` store)
  - MCP streamable tools (`get_adk_streamable_mcps()`)
  - custom Mongo tools (`get_service_details_by_service_id`, `get_resource_by_cpe_id`, `get_operation_mapping`, `get_transaction`, `get_service_specification`)
  - log analysis tools (`analyze_logs`, `validate_cpe_events`)
- Challenger has `after_agent_callback` which schedules memory reflection.

## Domain Knowledge Source

Prompt-hub instructions (markdown):

- `ProvisioningManagerInvestigator_Instruction.md`
- `ProvisioningManagerChallenger_Instruction.md`

These contain large domain playbooks, decision trees, and RCA guidance.

## MCP and Tool Surface

Primary MCP config: `mcp-config.json`

Configured toolsets include endpoints for:

- provisioning service
- device manager
- activation configuration
- capability manager
- resource inventory
- wifi mesh

This means provisioning domain reasoning can pull cross-system evidence directly.

## Data and State Dependencies

- Depends on session metadata (`tenant`, `environment`) for Mongo DB mapping.
- Uses profile-based database name map in `dt-mcp-tool`.
- Uses `MCP_CONFIG_PATH` for toolset bootstrap.
- Uses `ADK_SESSION_DB_URL` for resumable sessions.
- Uses `POSTGRES_MEMORY_DB_URL` optionally for memory store persistence.

## Strengths in Current Design

- Strong evidence-oriented troubleshooting architecture.
- Built-in self-critique loop (Investigator -> Challenger).
- Hybrid retrieval: MCP live calls + log analysis + memory search.
- Domain prompts are detailed and operationally rich.

## Constraints and Observations

- Domain knowledge is still prompt-embedded (hard to version/query as structured memory).
- Agent behavior quality depends heavily on instruction quality and tool reliability.
- Some repo artifacts (README, local config) are sparse or environment-dependent.

## Fit in Your Architecture

This agent already matches your domain-agent concept:

- clear bounded domain (provisioning)
- rich domain tools
- RCA-oriented behavior
- candidate for future self-healing workflows with explicit HIL gates
