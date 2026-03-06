# Current Agent Code Understanding

This folder captures a structured understanding of the current code across:

1. Framework layer: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/platform`
2. Agents layer: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/agents/onebb-backend/agents`
3. Evals layer: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/evals`

The intent is to document how the current system works today so we can evolve architecture with clarity.

## Reading Order

1. [00-overview-and-scope.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/00-overview-and-scope.md)
2. [01-platform-framework-layer.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/01-platform-framework-layer.md)
3. [02-agents-repo-inventory.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/02-agents-repo-inventory.md)
4. [03-runtime-flow-end-to-end.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/03-runtime-flow-end-to-end.md)
5. [04-domain-agent-provisioning-manager.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/04-domain-agent-provisioning-manager.md)
6. [05-domain-agent-wifi-mesh.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/05-domain-agent-wifi-mesh.md)
7. [06-prompt-hub-and-knowledge-model.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/06-prompt-hub-and-knowledge-model.md)
8. [07-evals-current-state.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/07-evals-current-state.md)
9. [08-observed-gaps-and-risks.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/08-observed-gaps-and-risks.md)
10. [09-provisioning-knowledge-model-v1.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/09-provisioning-knowledge-model-v1.md)
11. [questions.md](/Users/fracon/Documents/code/exploration/ai-agent/graph-vector/cognee/my-understanding/current-agent-code-understanding/questions.md)

## Quick Summary

- Current runtime is Google ADK + A2A communication with registry-based discovery.
- Planner writes execution plan into shared session state.
- Executor reads plan and dispatches to remote domain agents.
- Provisioning Manager and Wifi Mesh are domain agents.
- Domain knowledge is mostly embedded in prompt instructions (Prompt Hub + local instruction files).
- Evals are in progress and currently focused on Planner and Executor behavior.
