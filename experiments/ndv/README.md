# NDV Native LLM Switching MVP

## Status

- `ARCHITECTURE=FROZEN`
- `REUSE_ONLY=ACTIVE`
- `ENGINEERING_VALIDATION=SUPPORTED`
- `PRODUCT_MVP=NOT_REACHED`
- `VALIDATION_BLOCK=CLOSED`
- `EVIDENCE_BUNDLE=CLOSED`
- `NEXT_PROVIDER_TESTS=0`

The engineering switching path is validated, but the project has not yet reached a product MVP. A scientific treatment-effect comparison
between E0 and E1 has not been established because provider-backed experiments
were blocked by external capacity/rate-limit conditions.

## Current product status

The earlier `ENGINEERING_MVP=SUPPORTED` label is superseded by:

- `ENGINEERING_VALIDATION=SUPPORTED`
- `PRODUCT_MVP=NOT_REACHED`

The validated result is an engineering capability: native OpenHands LLM
switching works end to end through the benchmark integration.

A product MVP still requires an explicit product surface, user workflow,
acceptance criteria, and end-to-end value proposition beyond the benchmark
validation performed here.

## Architecture

NDV follows:

`REUSE -> ADAPT -> WRAP -> FORK -> BUILD`

Current state: `REUSE_ONLY`.

Rejected paths:

- custom runtime
- custom router
- custom switch runtime
- custom trace schema

Runtime behavior is provided by upstream OpenHands primitives:
`SwitchLLMTool`, `SwitchLLMAction`, `ConversationState`, the native LLM profile
store/registry, native metrics/telemetry, and LiteLLM transport.

NDV custom runtime code: `ZERO`.

## Pins

- OpenHands SDK: `43376f1868ffd702746080714a59c16d3f69ec12`
- benchmark baseline: `405bae7140d7e961a75f4910a0b2e7069731db96`
- branch: `ndv/e1-switch-llm-v6`

## E0 / E1

E0 exposes no native `SwitchLLMTool`.

E1 starts on A, provisions B in the native profile store, exposes exactly one
native `SwitchLLMTool`, and leaves the switching decision to the agent. No
custom switching mechanism is introduced.

B usage ID: `profile:<profile_name>`.

History and metrics remain native:

- `list(conversation.state.events)`
- `conversation.conversation_stats.get_combined_metrics()`

Harness controls:

- `enable_switch_llm`
- `switch_llm_profile_name`
- `switch_llm`
- `--enable-switch-llm`
- `--switch-llm-config-path`
- `--switch-llm-profile-name`

Implementation files:

- `benchmarks/swebench/run_infer.py`
- `benchmarks/utils/args_parser.py`
- `benchmarks/utils/models.py`

## Native switching contract

Validated behavior:

1. active model invokes `switch_llm`
2. tool emits `SwitchLLMAction(profile_name, reason)`
3. executor uses the native conversation profile switch
4. switch applies to the next LLM call
5. observation exposes the active model
6. agent and `ConversationState` reflect B

Deterministic evidence establishes:

- E0 has no `SwitchLLMTool`
- E1 has exactly one native `SwitchLLMTool`
- native action switches A -> B
- agent and state update to B
- `profile:alternate` exists in the native registry
- a missing profile leaves A unchanged

## Tests

Normative tests:

- `tests/test_swebench_switch_llm.py`
- `tests/test_swebench_switch_llm_live_profile.py`
- `tests/test_swebench_switch_llm_ndv_contract.py`

Recorded validation:

- native switch regression: `26/26 PASS`
- NDV contract tests: `PASS`

## Provider-backed evidence

OpenRouter classification:

- `OPENROUTER_E0_E1=BLOCKED_EXTERNAL_CAPACITY`
- `HARNESS_FAULT_DEMONSTRATED=NO`
- `SWITCH_WIRING_FAULT_DEMONSTRATED=NO`
- `SCIENTIFIC_COMPARISON=NOT_AVAILABLE`

Gemini engineering validation:

- `REST_A_B=PASS`
- `FUNCTION_CALLING_A_B=PASS`
- `OPENHANDS_LLM_A_B=PASS`
- `AGENT_TRAJECTORY_A_B=PASS`
- `NATIVE_REAL_SWITCH_A_TO_B=PASS`

Validated real path:

`REAL_A_TOOL_CALL -> NATIVE_SWITCH_LLM -> REAL_B_CALL`

Normative evidence:

- `experiments/ndv/e0-e1-r1-r4-evidence.md`
- `experiments/ndv/gemini-g1-g4-evidence.md`
- `experiments/ndv/upstreamability-assessment.md`

Historical, non-normative artifacts:

- `experiments/e01-smoke.txt`
- `experiments/e02-controlled-3.txt`

## Scientific status

- `ENGINEERING_VALIDATION=SUPPORTED`
- `PRODUCT_MVP=NOT_REACHED`
- `SCIENTIFIC_EFFECT_OF_SWITCH=NOT_ESTABLISHED`

Invalid provider arms must not be used for causal comparison of tokens, cost,
completion behavior, or benchmark outcome.

## Rerun policy

Current provider-test budget: `NEXT_PROVIDER_TESTS=0`.

Do not rerun Django, Pylint, Sphinx, OpenRouter, or Gemini provider experiments
without a new explicit hypothesis, an explicit test budget, clear information
gain, and adequate provider capacity.

Keep the existing API key. Do not create a new key.

## Scope boundary

This engineering validation does not claim that switching improves benchmark performance, cost,
token usage, or completion rate.

It establishes that native OpenHands LLM switching can be exposed through a
thin benchmark patch and exercised end to end without an NDV-specific switching
runtime.

Eligible next work:

- release packaging
- technical handoff
- code review
- upstreamability assessment
- clearly justified cleanup
- future scientific E0/E1 work only when capacity and budget justify it
