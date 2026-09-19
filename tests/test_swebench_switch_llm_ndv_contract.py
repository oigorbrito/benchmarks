from pathlib import Path

import pytest

from benchmarks.swebench.run_infer import get_default_tool_names
from openhands.sdk import LocalConversation
from openhands.sdk.agent import Agent
from openhands.sdk.context.prompts import prompt as prompt_module
from openhands.sdk.llm import llm_profile_store
from openhands.sdk.llm.llm_profile_store import LLMProfileStore
from openhands.sdk.testing import TestLLM
from openhands.sdk.tool.builtins import (
    SwitchLLMAction,
    SwitchLLMObservation,
)


def _llm(model: str, usage_id: str):
    return TestLLM.from_messages([], model=model, usage_id=usage_id)


@pytest.fixture(autouse=True)
def isolated_openhands_home(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    home = tmp_path / "home"
    home.mkdir()

    monkeypatch.setenv("HOME", str(home))

    # prompt.py derives its Jinja bytecode cache from expanduser("~").
    # Clear cached environments so each test resolves the isolated HOME.
    prompt_module._get_env.cache_clear()
    prompt_module._get_template.cache_clear()

    yield

    prompt_module._get_env.cache_clear()
    prompt_module._get_template.cache_clear()


@pytest.fixture()
def isolated_profile_store(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> LLMProfileStore:
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()
    monkeypatch.setattr(
        llm_profile_store,
        "_DEFAULT_PROFILE_DIR",
        profile_dir,
    )
    return LLMProfileStore(base_dir=profile_dir)


def test_ndv_e0_does_not_expose_switch_llm_tool() -> None:
    assert "SwitchLLMTool" not in get_default_tool_names(enable_switch_llm=False)


def test_ndv_e1_exposes_exactly_one_native_switch_llm_tool() -> None:
    tools = get_default_tool_names(enable_switch_llm=True)
    assert tools.count("SwitchLLMTool") == 1


def test_ndv_native_switch_action_rebinds_agent_and_state(
    isolated_profile_store: LLMProfileStore,
    tmp_path: Path,
) -> None:
    isolated_profile_store.save(
        "alternate",
        _llm("model-b", "profile:alternate"),
    )

    conversation = LocalConversation(
        agent=Agent(
            llm=_llm("model-a", "agent"),
            tools=[],
            include_default_tools=["SwitchLLMTool"],
        ),
        workspace=tmp_path,
        visualizer=None,
    )

    assert conversation.agent.llm.model == "model-a"

    observation = conversation.execute_tool(
        "switch_llm",
        SwitchLLMAction(
            profile_name="alternate",
            reason="NDV deterministic integration proof",
        ),
    )

    assert isinstance(observation, SwitchLLMObservation)
    assert not observation.is_error
    assert observation.active_model == "model-b"
    assert conversation.agent.llm.model == "model-b"
    assert conversation.state.agent.llm.model == "model-b"

    registered = conversation.llm_registry.get("profile:alternate")
    assert registered.model == "model-b"
    assert registered.usage_id == "profile:alternate"


def test_ndv_missing_profile_preserves_model_a(
    isolated_profile_store: LLMProfileStore,
    tmp_path: Path,
) -> None:
    conversation = LocalConversation(
        agent=Agent(
            llm=_llm("model-a", "agent"),
            tools=[],
            include_default_tools=["SwitchLLMTool"],
        ),
        workspace=tmp_path,
        visualizer=None,
    )

    observation = conversation.execute_tool(
        "switch_llm",
        SwitchLLMAction(
            profile_name="missing",
            reason="negative NDV contract proof",
        ),
    )

    assert isinstance(observation, SwitchLLMObservation)
    assert observation.is_error
    assert conversation.agent.llm.model == "model-a"
    assert conversation.state.agent.llm.model == "model-a"
