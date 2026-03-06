# Transitional Evaluations Strategy for Domain Knowledge

As we transition from prompt-embedded domain knowledge to a structured, knowledge-first architecture, our evaluation strategy must shift to focus explicitly on **retrieval quality** and **tool selection**.

Before we can trust an agent to execute an action (e.g., provisioning a service), we must verify that it has retrieved the correct business processing (BP) rules and constraints from the new knowledge model.

This document outlines the evaluation strategy for the knowledge retrieval layer, specifically focusing on the initial transition phase where the priority is simply getting the BP knowledge out of the codebase.

## 1. Goal of Transitional Evals

The primary goal is to answer this question: **Given a specific operational scenario, does the agent retrieve the correct domain knowledge constraint before deciding on its next action?**

Secondary goal: **Does the retrieved static BP knowledge successfully guide the agent to use the right MCP tools to access the current live state?**

## 2. Evaluation Strategy Framework

> **Note on Evaluation Framework:** For these tests, we will default to using [DeepEval](https://github.com/confident-ai/deepeval) as our evaluation framework, unless we discover a solid technical reason not to use it as we proceed. DeepEval provides robust metrics for retrieval accuracy and LLM trace evaluations.

To verify the quality of retrieval without executing destructive actions, we need a two-stage evaluation pipeline:

### Stage 1: Retrieval Accuracy Evaluation
This stage tests purely if the Knowledge Graph (or database) returns the correct subset of domain rules based on a user's intent.

*   **Test Input:** An isolated user prompt (e.g., "The customer is a VIP and needs a new mesh node. What are the rules?").
*   **Expected Output:** The exact BP rule or document ID from the knowledge base (e.g., `rule_vip_mesh_provisioning_v2`).
*   **Eval Metric:** Precision & Recall. Did it pull the right rule? Did it miss any required rules? Did it pull irrelevant garbage?

### Stage 2: Tool Selection Evaluation
This stage tests whether the LLM, having received the *correct* static BP knowledge, successfully decides to use the correct MCP tools to fetch the required live state (databases, logs) to satisfy the rule.

*   **Test Input:** The user prompt + the *mocked* correct BP knowledge injected directly into context.
*   **Expected Output:** The exact sequence of MCP tool calls (e.g., `call: check_vip_status()`, then `call: get_mesh_inventory()`).
*   **Eval Metric:** Tool selection accuracy and sequence order. Did it try to execute without checking the required live state defined by the BP rule?

## 3. How to Write These Evals

When a new piece of domain knowledge (like a provisioning workflow) is modeled, follow these steps:

1.  **Extract the Rules:** Identify the core, static business logic. (e.g., "If VIP, then use expedited queue").
2.  **Define the Test Case Matrix:**
    *   Create 5-10 varied inputs (user utterances, system alerts) that should trigger this specific rule.
    *   Create 5-10 negative inputs that should *not* trigger the rule to test boundaries.
3.  **Write the Eval Script:**
    *   Initialize the agent in a sandbox environment where the knowledge base is populated, but MCP execution tools (like `provision_service`) are mocked to return success without acting.
    *   Assert that the *trace* of the agent's thought process includes a query to the knowledge base that returns the target rule.
    *   Assert that the *subsequent action* is a query to the relevant MCP state tool (e.g., `check_database_state`), rather than an immediate, blind provisioning execution.

## 4. End-to-End Test Alignment

The ultimate proof of the knowledge model is the end-to-end (E2E) test.

In E2E testing, the assertion is: **Static BP Knowledge + Live Database State = Correct Decision.**

The evaluation framework must mock the live database state to various edge cases (e.g., DB says "down", DB says "active") and verify that the agent, guided by the static BP knowledge, makes the correct final decision (e.g., "Abort provisioning because the required node is down, per Rule X").