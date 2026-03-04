# Agent Quick Start for `my-understanding`

Use this as a working guide when adding or updating documentation in this folder.

## Purpose

This folder is the working knowledge base for architecture understanding, decisions, and open questions.

## Current Priority Focus

Until changed explicitly, prioritize knowledge-building topics:

- domain knowledge
- conversation history
- learnings
- other reusable knowledge artifacts

When a question is outside this focus, mark it deferred instead of expanding scope.

## Status Notation (Mandatory)

Use these markers in question trackers:

- `[ ]` Open
- `[x]` Closed
- `[-]` Deferred

For each tracked question, include:

- a clear `Answer:` block when information is available
- status update based on that answer (`[ ]` -> `[x]` or `[-]`)

## Answer Preservation Rule (Mandatory)

- Do not delete user-provided answers.
- You may format, reorganize, or normalize wording for clarity, but preserve original intent.
- If an answer is partial, keep it and add follow-up questions instead of replacing it.

## Follow-up Numbering Rule

- Keep the parent question number unchanged.
- Add follow-up questions using hierarchical numbering:
1. `18.1`
2. `18.1.1`
3. `18.2`
- Use this pattern whenever deeper clarification is required.

## Deferral Rule

Mark as `[-] Deferred` when:

- question is valid but outside current focus
- decision is intentionally postponed
- dependency decision is not yet ready

Do not delete deferred questions. Keep them visible for future reopening.

## Documentation Conventions

- Keep files short, structured, and easy to scan.
- Prefer one topic per file.
- Keep implementation references concrete (file paths, module names, runtime behavior).
- Record assumptions explicitly.
- Keep questions in tracker format with status notation.

## Working Boundaries

- Treat external repos as read-only unless explicitly asked to modify.
- For this workspace, update only `my-understanding` docs unless told otherwise.
- If code appears locally inconsistent/uncommitted, document uncertainty rather than forcing conclusions.

## Suggested Workflow for New Work

1. Read existing relevant notes first.
2. Add/update understanding docs with concrete evidence.
3. Update question tracker with statuses.
4. Keep non-focus items deferred.
5. Link new docs from index READMEs.

## Current Architecture Context (Reference)

- Orchestration stack: Google ADK + A2A
- Control agents: Orchestrator, Planner, Executor, QuerySense
- Domain agents in scope: Provisioning Manager, Wifi Mesh
- Current domain knowledge pattern: mostly prompt-embedded (Prompt Hub + local instruction files)
