# 06 - Prompt Hub and Current Knowledge Model

## Core Observation

Current domain knowledge is primarily embedded in prompts/instructions, not in an external structured memory layer.

This matches your note: prompt hub currently holds domain knowledge directly in prompt files.

## Knowledge Locations

### A) Prompt Hub (`dt-prompt-hub`)

Path:

- `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/platform/platform-ai-core/dt-prompt-hub`

Key files:

- `QuerySense_Instruction.md`
- `ProvisioningManagerInvestigator_Instruction.md`
- `ProvisioningManagerChallenger_Instruction.md`
- `LogAnalyzer_Instruction.md`
- `EventAnalyzer_Instruction.md`
- `RequestClassifier_Instruction.md`

Loader:

- `instructions.py` scans `*_Instruction.md` and serves via `get_instruction(name)`.

### B) Agent-local instruction files

- Planner: `planner-agent/src/planner_agent/instructions.py`
- Wifi Mesh: `wifi-mesh-agent/src/wifi_mesh_agent/instructions.py`

These are large static instruction blocks encoded directly in code.

### C) Emerging memory utilities

Provisioning Manager also uses:

- `dt-agent-memory` memory search tool
- reflection callback to convert events into memory entries

But this is additive and does not replace prompt-embedded domain guidance yet.

## Practical Meaning

Current knowledge stack is hybrid but prompt-first:

1. Prompt instructions drive reasoning policy.
2. MCP/domain tools fetch live data.
3. Optional memory retrieval supplements context.

So behavior quality depends significantly on instruction completeness and maintenance.

## Strengths of Current Approach

- Fast iteration for domain logic updates.
- Easy to enforce behavior constraints and output formats.
- Keeps routing/policy explicit.

## Limitations of Current Approach

- Prompt versioning and auditability can become hard as prompt files grow.
- Knowledge reuse across agents is uneven when instructions are duplicated.
- Harder to query or govern domain knowledge as reusable facts.
- Testing prompt changes requires strong eval discipline.

## Implication for Next Architecture Phase

Your future direction (shared memory graph/vector + domain agents) can gradually externalize knowledge from static prompts to managed memory while keeping prompts as policy/behavior guardrails.

A likely transition path:

1. Keep prompts for role/rules.
2. Move volatile domain facts and learnings to memory layer.
3. Keep tool schemas and action constraints explicit in prompts.
