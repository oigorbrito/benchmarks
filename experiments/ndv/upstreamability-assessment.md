# NDV Upstreamability Assessment

## Status

`UPSTREAMABILITY_ASSESSMENT=CLOSED`

Final classification:

`PATCH_STATUS=UPSTREAMABLE_WITH_MINOR_CLEANUP`

This assessment concerns the benchmark integration only. It does not reopen the
provider-validation block and does not change the frozen NDV architecture.

## Architecture assessment

The patch remains consistent with the NDV reuse doctrine:

- `HARNESS_ARCHITECTURE=UPSTREAMABLE`
- `PROFILE_API_PATH=CORRECT`
- `PROFILE_STORE_REUSE=NO_DUPLICATE_HELPER_FOUND`
- `RUNTIME_REIMPLEMENTATION=NO`
- `CUSTOM_ROUTER=NO`
- `CUSTOM_SWITCH_RUNTIME=NO`
- `DEFAULT_BEHAVIOR_PRESERVED=YES`

The benchmark exposes and configures the native OpenHands switching mechanism.
It does not implement an NDV-specific switching runtime.

## Upstream candidates

Production files suitable for an upstream proposal after minor cleanup:

- `benchmarks/swebench/run_infer.py`
- `benchmarks/utils/args_parser.py`
- `benchmarks/utils/models.py`

The feature is opt-in through `enable_switch_llm=False` by default, preserving
the existing benchmark behavior when switching is not enabled.

The profile API paths used by the patch are:

- `GET /api/profiles`
- `POST /api/profiles/{profile_name}`

Repository review found no existing benchmark helper duplicating this
provisioning path.

## Test classification

Potentially upstreamable regression tests:

- `tests/test_swebench_switch_llm.py`
- `tests/test_swebench_switch_llm_live_profile.py`

NDV-specific contract/evidence test:

- `tests/test_swebench_switch_llm_ndv_contract.py`

The NDV-specific contract test should remain in the fork or be reduced to
generic regression cases before any upstream proposal.

## NDV-only artifacts

The following are project evidence or historical development artifacts and
should not be part of an upstream feature patch:

- `experiments/ndv/README.md`
- `experiments/ndv/e0-e1-r1-r4-evidence.md`
- `experiments/ndv/gemini-g1-g4-evidence.md`
- `experiments/ndv/upstreamability-assessment.md`
- `experiments/e01-smoke.txt`
- `experiments/e02-controlled-3.txt`

## Minor cleanup before an upstream PR

The closed engineering validation does not require these changes. They are recommended only
for preparation of a future upstream proposal.

### Configuration validation

`run_infer.py` currently relies on assertions after the switch feature is
enabled to establish that the alternate profile name and LLM configuration are
present.

For upstream code, invalid combinations should preferably be rejected through
explicit configuration validation rather than `assert`.

### Naming

The metadata field:

`switch_llm: LLM | None`

contains an alternate LLM configuration, while its name can be read as an
action or boolean.

A future upstream cleanup may use a more explicit name such as
`switch_llm_config` or `alternate_llm`.

This is an API-quality recommendation, not a correctness defect.

### CLI consistency

A future upstream version should explicitly validate combinations such as:

- `--enable-switch-llm` without `--switch-llm-config-path`
- switching requested for an unsupported non-default agent type

### Tool symbol

The implementation currently includes the literal tool name
`"SwitchLLMTool"`.

If the pinned SDK exposes a stable canonical symbol suitable for this purpose,
a future upstream cleanup may derive the name from that symbol rather than
duplicating the string.

No new abstraction should be introduced solely for this cleanup.

## Conclusion

The feature implementation is structurally suitable for upstream consideration.

Its core properties are:

- native OpenHands switch semantics
- no custom router
- no custom switching runtime
- native profile store
- native conversation state
- native telemetry
- opt-in/default-preserving benchmark behavior
- bounded production patch

Therefore:

`PATCH_STATUS=UPSTREAMABLE_WITH_MINOR_CLEANUP`

No PR is opened by this assessment.
