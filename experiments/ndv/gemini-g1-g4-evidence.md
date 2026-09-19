# NDV Gemini engineering validation — G1 through G4

## Scope

This evidence records the Gemini alternative-provider engineering validation.
It is separate from the frozen OpenRouter E0/E1 experiment and does not
establish a SWE-bench treatment effect.

Pins:
- OpenHands SDK: `43376f1868ffd702746080714a59c16d3f69ec12`
- benchmark baseline: `405bae7140d7e961a75f4910a0b2e7069731db96`
- branch: `ndv/e1-switch-llm-v6`

Architecture remains upstream-only: native `SwitchLLMTool`,
`SwitchLLMAction`, `ConversationState`, LLM profile store/registry, and
LiteLLM transport. No NDV custom router or switching runtime was added.

## Qualified Gemini pair

- A: `gemini-3.1-flash-lite`
- B: `gemini-3.5-flash-lite`

LiteLLM/OpenHands identifiers:
- `gemini/gemini-3.1-flash-lite`
- `gemini/gemini-3.5-flash-lite`

## G1 — authentication and direct inference

Gemini authentication/model discovery passed with the existing key.
`API_KEY_ACTION=KEEP`
Direct inference succeeded for the final A/B pair.

## G2 — sequential stability and function calling

A (`gemini-3.1-flash-lite`):
- sequential inference: 5/5 PASS
- forced `switch_llm` function call: PASS

Rejected B candidate (`gemini-3.5-flash`):
- sequential inference: 4/5
- HTTP 503 `UNAVAILABLE` observed
- forced function call: HTTP 503 / FAIL

Classification: `REJECTED_EXTERNAL_CAPACITY`

Replacement B (`gemini-3.5-flash-lite`):
- sequential inference: 5/5 PASS
- forced `switch_llm` function call: PASS

## G3 — OpenHands integration

OpenHands LLM transport:
- A returned `NDV_OPENHANDS_OK`, metrics present, PASS
- B returned `NDV_OPENHANDS_OK`, metrics present, PASS

`G3B_OPENHANDS_LLM=PASS`
`G3C_AGENT_TRAJECTORY=PASS`

Native real A -> B switching:
- A emitted native `switch_llm`
- observation type: `SwitchLLMObservation`
- `is_error=False`
- requested profile: `alternate`
- active model became `gemini/gemini-3.5-flash-lite`
- agent model and ConversationState model both moved to B
- next real inference returned `NDV_SWITCHED_TO_B_OK`
- usage IDs observed: `ndv:g3d:a`, `profile:alternate`
- A metrics gate: PASS
- B metrics gate: PASS
- registry `profile:alternate` resolved to B

`G3D_NATIVE_SWITCH=PASS`

Validated path:
`REAL_A_TOOL_CALL -> NATIVE_SWITCH_LLM -> REAL_B_CALL`

## G4 — SWE-bench harness

Instance: `django__django-11477`

### Short paired run — max_iterations=6

E0:
- provider gate: PASS
- metrics present: YES
- termination: `MaxIterationsReached`
- prompt tokens: 112382
- completion tokens: 218

E1:
- provider gate: PASS
- metrics present: YES
- termination: `MaxIterationsReached`
- prompt tokens: 114544
- completion tokens: 834
- persisted switch event observed: NO

Both arms hit the deliberately low iteration ceiling, so this run is not
valid treatment-effect evidence.

### R2 paired run — max_iterations=30

E0:
- output kind: ERROR
- error: `Remote conversation ended with error`
- provider error detected: FALSE
- metrics present: YES
- prompt tokens: 251225
- completion tokens: 1984
- completion gate: FAIL
- provider gate: PASS

E1:
- output kind: ERROR
- explicit `LLMRateLimitError`
- provider error detected: TRUE
- metrics present: YES
- prompt tokens: 233412
- completion tokens: 529
- persisted switch event observed: NO
- completion gate: FAIL
- provider gate: FAIL

Classification: `G4_R2_INVALID_FOR_SCIENTIFIC_COMPARISON`

The arms failed for different reasons. Token, cost, patch, or behavioral
differences from this pair must not be interpreted as a causal switching effect.

## Conclusions

Engineering validation:

```text
REST_A_B=PASS
FUNCTION_CALLING_A_B=PASS
OPENHANDS_LLM_A_B=PASS
AGENT_TRAJECTORY_A_B=PASS
NATIVE_REAL_SWITCH_A_TO_B=PASS
HARNESS_FAULT_DEMONSTRATED=NO
SWITCH_WIRING_FAULT_DEMONSTRATED=NO
ENGINEERING_MVP=SUPPORTED
```

Scientific validation:

```text
OPENROUTER_E0_E1=BLOCKED_EXTERNAL_CAPACITY
GEMINI_SCIENTIFIC_E0_E1=BLOCKED_EXTERNAL_CAPACITY
SCIENTIFIC_EFFECT_OF_SWITCH=NOT_ESTABLISHED
```

## Test-budget decision

No further provider calls are authorized for this validation block.

```text
NEXT_PROVIDER_TESTS=0
DJANGO_RERUN=DEFERRED
PYLINT=DEFERRED
SPHINX=DEFERRED
API_KEY_ACTION=KEEP
```

Future provider testing requires a new explicit hypothesis and test budget.
