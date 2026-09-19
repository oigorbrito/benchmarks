# NDV E0/E1 empirical evidence — R1 through R4

## Frozen implementation

- OpenHands SDK: `43376f1868ffd702746080714a59c16d3f69ec12`
- benchmark baseline: `405bae7140d7e961a75f4910a0b2e7069731db96`

Controlled sample:

- `django__django-11477`
- `pylint-dev__pylint-6386`
- `sphinx-doc__sphinx-9229`

E0 disables native `SwitchLLMTool`.

E1 starts on model A, provisions profile B, and exposes the native
`SwitchLLMTool`. Switching remains agent-selected.

## R1

INVALID.

Cause: benchmark/local SDK image-tag contract skew.

Operational correction: `IMAGE_TAG_PREFIX=43376f1`.

No switching-runtime change required.

## R2

INVALID.

Cause: authentication absent from the execution environment.

A later authenticated probe proved real inference, token accounting,
latencies and response IDs.

No structural benchmark authentication defect was demonstrated.

## R3

INVALID.

- attempted: 6/6
- auth gate: PASS
- image gate: PASS
- rate-limit affected: 6/6
- auth errors: 0/6
- image errors: 0/6

Classification:

`PROVIDER_RATE_LIMIT_ALL_TRAJECTORIES`

R3 E0/E1 numerical deltas are not valid treatment-effect evidence.

## R4 paired Django isolation

INVALID.

Preflight had:

- valid OpenRouter authentication
- `/api/v1/key` HTTP 200
- `usage_daily = 0`
- free-tier account

Result:

- E0 rate-limit affected: YES
- E1 rate-limit affected: YES

Pylint and Sphinx were intentionally not executed.

## Scientific status

The frozen OpenRouter-free experiment does not currently provide a valid
E0/E1 comparison.

This does not demonstrate failure of native:

- `SwitchLLMTool`
- `SwitchLLMAction`
- LLM profile persistence
- ConversationState model switching

The demonstrated blocker is external provider capacity/rate limiting.

## Deterministic integration evidence

NDV tests prove:

- E0 does not expose `SwitchLLMTool`
- E1 exposes exactly one native `SwitchLLMTool`
- native `SwitchLLMAction` switches A -> B
- agent and ConversationState both move to B
- `profile:alternate` is present in the native LLM registry
- missing profile leaves model A unchanged

The pinned SDK already supplies broader native regression coverage for
profile switching, state synchronization, registry reuse, error behavior
and switching during `arun()`.

## MVP implication

OpenRouter free capacity is an external validation blocker, not an
architectural blocker.

No further OpenRouter run should be attempted unless capacity conditions
materially change.
