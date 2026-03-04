# 01 - Platform Framework Layer

This note summarizes framework modules that are actively used by current agents.

## 1) Agent Communication Layer (`dt-agent-communication`)

Primary role: expose ADK agents through A2A protocol and registry registration.

Key behavior:

- `enable_agent_communication(...)` decorator wraps an agent factory and returns an A2A app.
- Default strategy is `ADKA2ACommunication`.
- App includes plugins: `ErrorHandlingPlugin`, `SessionStateInjectorPlugin`, `HILToolPlugin`.
- App enables resumability + event compaction summarization.
- On startup, app auto-registers into Agent Registry.

Key files:

- `platform-ai-agentic/dt-agent-communication/src/dt_agent_communication/decorator/agent_decorator.py`
- `platform-ai-agentic/dt-agent-communication/src/dt_agent_communication/providers/a2a/google_adk.py`
- `platform-ai-agentic/dt-agent-communication/src/dt_agent_communication/providers/a2a/runner_with_compaction_event.py`
- `platform-ai-agentic/dt-agent-communication/src/dt_agent_communication/adk_agents/PlatformRemoteA2AAgent.py`

Important detail:

- `PlatformRemoteA2AAgent` forwards only last message part and uses session id as context id.

## 2) Agent Registry (`dt-agent-registry`)

Primary role: dynamic registry of online agents + agent cards.

Key behavior:

- `/register`: stores agent URL + tags + online status + last_seen timestamp.
- `/agents`: returns agent cards and tags.
- `/refresh`: refreshes one/all agent cards.
- Background staleness task marks agents offline if heartbeat is stale.
- In-memory state storage.

Key file:

- `platform-ai-agentic/dt-agent-registry/src/dt_agent_registry/registry.py`

## 3) MCP Tool Layer (`dt-mcp-tool`)

Primary role: central tool loading and tool wrappers for planners/domain agents.

Core parts:

- `get_adk_streamable_mcps()`: reads `MCP_CONFIG_PATH` and builds MCP toolsets.
- `discover_registered_agents()`: fetches registry agents for routing (filters out agents tagged with `Service`).
- `set_execution_plan(...)`: writes execution plan into custom session state.
- Domain data helper tools: `get_service_details_by_service_id`, `get_resource_by_cpe_id`, `get_operation_mapping`, `get_transaction`, log analyzer tools.

Key files:

- `platform-ai-core/dt-mcp-tool/src/dt_mcp_tool/__init__.py`
- `platform-ai-core/dt-mcp-tool/src/dt_mcp_tool/providers/google_adk/toolset_builder.py`
- `platform-ai-core/dt-mcp-tool/src/dt_mcp_tool/tools/discover_agents.py`
- `platform-ai-core/dt-mcp-tool/src/dt_mcp_tool/tools/set_execution_plan.py`
- `platform-ai-core/dt-mcp-tool/src/dt_mcp_tool/tools/*.py`

Important detail:

- MCP header provider injects session metadata and tracing/auth headers dynamically.

## 4) Session and Utility Layer (`dt-utils`)

Primary role: registration helpers + extended session persistence.

Key behavior:

- Registry heartbeat (`start_registry_heartbeat`) periodically re-registers agents.
- `CustomSessionService` extends ADK DB session service with `custom_states` table.
- Planner and Executor depend on this shared custom session state for execution flow.

Key files:

- `platform-ai-core/dt-utils/src/dt_utils/register_loop.py`
- `platform-ai-core/dt-utils/src/dt_utils/registry_utils.py`
- `platform-ai-core/dt-utils/src/dt_utils/custom_database_session_service.py`

## 5) Prompt Hub (`dt-prompt-hub`)

Primary role: loads prompt/instruction markdown files by name.

Key behavior:

- Loads `*_Instruction.md` files into in-memory dictionary.
- `get_instruction(name)` is case-insensitive and appends `_instruction` suffix.

Key files:

- `platform-ai-core/dt-prompt-hub/src/dt_prompt_hub/instructions.py`
- `platform-ai-core/dt-prompt-hub/src/dt_prompt_hub/*_Instruction.md`

## 6) Model Provider (`dt-model-provider`)

Primary role: centralized LLM client factory.

Key behavior:

- `get_llm()` returns cached LiteLlm client.
- Azure provider reads deployment/base/api key from env/secrets.
- `get_chat_lite_llm()` used by log analyzer and memory reflection.

Key files:

- `platform-ai-core/dt-model-provider/src/dt_model_provider/utils/factory.py`
- `platform-ai-core/dt-model-provider/src/dt_model_provider/providers/azure_provider.py`

## 7) Platform Plugins (`dt-platform-plugins`)

Primary role: ADK plugin hooks for errors, session metadata injection, and HIL.

Key behavior:

- `ErrorHandlingPlugin`: normalized tool/model error responses.
- `SessionStateInjectorPlugin`: injects A2A metadata into callback context state.
- `HILToolPlugin`: conditionally provides `ask_human` long-running tool to model.

Key files:

- `platform-ai-core/dt-platform-plugins/src/dt_platform_plugins/adk/error_handling_plugin.py`
- `platform-ai-core/dt-platform-plugins/src/dt_platform_plugins/adk/session_state_plugin.py`
- `platform-ai-core/dt-platform-plugins/src/dt_platform_plugins/adk/hil_tool_plugin.py`

## 8) Agent Memory Package (`dt-agent-memory`)

Primary role: optional memory reflection pipeline used by Provisioning Manager.

Key behavior:

- Initializes vector store (`InMemoryStore` or `PostgresStore`).
- Provides `after_agent_callback` that converts ADK events and schedules background reflection.

Key files:

- `platform-ai-agentic/dt-agent-memory/src/dt_agent_memory/store/langmem_store.py`
- `platform-ai-agentic/dt-agent-memory/src/dt_agent_memory/callbacks/adk_agent_callback.py`

## 9) Framework Summary

Current platform is already designed as composable modules for:

- agent exposure (A2A)
- tooling integration (MCP)
- shared prompt loading
- shared model access
- shared session orchestration state
- optional memory reflection

This framework is mature enough for orchestration-heavy use cases, while domain intelligence is still prompt and tool driven.
