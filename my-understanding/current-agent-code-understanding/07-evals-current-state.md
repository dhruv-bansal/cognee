# 07 - Evals Current State

Repo reviewed: `/Users/fracon/Documents/code/onebb/digital/home/applications/ai/evals`

## Current Scope of Evals

Implemented package:

- `dt-evals`

Current evaluated agents:

- Planner Agent
- Executor Agent

Not yet covered directly by dedicated eval suites:

- Orchestrator Agent
- Query Sense Agent (as standalone target)
- Provisioning Manager domain quality
- Wifi Mesh domain quality

## Framework Characteristics

- Uses DeepEval (`deepeval`) with custom runners.
- Uses A2A protocol client (`AgentRunner`) to call running agents over HTTP.
- Supports YAML config for agent URLs and metric thresholds.
- Includes parser adapters for planner and executor A2A payload formats.

Key files:

- `dt-evals/src/dt_evals/utils/agent_runner.py`
- `dt-evals/src/dt_evals/utils/a2a_response_parser.py`
- `dt-evals/src/dt_evals/config/agent-config.yml`
- `dt-evals/src/dt_evals/config/metrics-config.yml`

## Planner Eval Coverage

Datasets:

- routing dataset
- conversational dataset
- state dataset (present in datasets folder)

Metrics:

- Routing Correctness
- Tool Usage Correctness
- State Detection
- Conversational Quality

Test files:

- `planner_agent/tests/test_routing.py`
- `planner_agent/tests/test_conversational.py`

## Executor Eval Coverage

Datasets:

- execution dataset
- error handling dataset
- multi-agent dataset

Metrics:

- Execution Plan Adherence
- Sub-Agent Dispatch Correctness
- Error Message Accuracy
- Response Completeness
- Orchestration Correctness

Test files:

- `executor_agent/tests/test_execution.py`
- `executor_agent/tests/test_error_handling.py`
- `executor_agent/tests/test_multi_agent.py`

## Important Runtime Dependency for Executor Evals

Executor tests seed execution plan into shared custom session DB before calling executor.

- Uses `session_seeder.py`
- Requires `ADK_SESSION_DB_URL` aligned with running executor environment.

## Current Maturity View

What is good:

- Good start on control-plane reliability checks (planner/executor).
- Datasets include single-agent and multi-agent scenarios.
- Error path assertions exist.

What is still open:

- End-to-end quality for domain agents themselves.
- Groundedness/factual correctness against real tool outputs.
- Orchestrator and QuerySense behavior as explicit test targets.
- Regression safety for prompt changes in domain instructions.
