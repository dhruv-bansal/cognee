# 05 - Domain Agent: Wifi Mesh

Folder: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/agents/onebb-backend/agents/wifi-mesh-agent`

## What This Agent Does

Wifi Mesh Agent handles wifi and mesh-related user operations:

- wifi network inspection
- wifi config changes
- guest wifi handling
- credentials and network state interactions
- mesh troubleshooting guidance

## Implementation Highlights

File: `src/wifi_mesh_agent/agent.py`

- Single `LlmAgent` (not sequential sub-agent chain).
- A2A-enabled and tagged as domain agent (`Onebb`, `Domain`).
- Uses only MCP streamable toolsets as runtime tools.
- Instructions and long domain behavior are in local `instructions.py`.

## Domain Knowledge Source

Unlike Provisioning Manager (Prompt Hub markdown), Wifi Mesh keeps behavior text directly in code:

- `src/wifi_mesh_agent/instructions.py`

This instruction defines capabilities, operating rules, response templates, and tool guidance.

## MCP and Tool Surface

Primary MCP config: `mcp-config.json`

Configured toolsets:

- `wifi_network`
- `provisioning_toolset` (with `getServiceDetails` filter)

This gives wifi context plus service-level lookup capability.

## Data and State Dependencies

- Depends on `MCP_CONFIG_PATH` to load toolset config.
- Depends on session metadata propagation for tenant/environment aware calls.
- Uses shared model provider and logging/tracing stack.

## Strengths in Current Design

- Clear domain scope.
- Action-oriented instruction set for wifi operations.
- Tooling is focused and simpler than provisioning domain.

## Constraints and Observations

- Domain knowledge is prompt text in Python file, not centralized in Prompt Hub.
- No explicit second-pass validation sub-agent (unlike provisioning).
- README is currently empty, so behavior is mostly discoverable from source.

## Fit in Your Architecture

This already fits your domain-agent model, especially for user-facing wifi workflows and controlled action execution once HIL gates are formalized.
