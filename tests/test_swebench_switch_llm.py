from unittest.mock import Mock

import pytest
from pydantic import SecretStr

from benchmarks.swebench.run_infer import (
    assert_empty_llm_profile_store,
    get_default_tool_names,
    provision_llm_profile,
)
from openhands.sdk import LLM
from openhands.sdk.llm.llm_profile_store import PROFILE_NAME_REGEX
from openhands.sdk.tool import BUILT_IN_TOOLS


def test_switch_llm_disabled_preserves_sdk_default_tools() -> None:
    expected = [tool.__name__ for tool in BUILT_IN_TOOLS]
    assert get_default_tool_names(enable_switch_llm=False) == expected


def test_switch_llm_enabled_adds_only_switch_tool() -> None:
    expected = [tool.__name__ for tool in BUILT_IN_TOOLS]
    actual = get_default_tool_names(enable_switch_llm=True)
    assert actual == [*expected, "SwitchLLMTool"]
    assert actual.count("SwitchLLMTool") == 1


def test_provision_llm_profile_uses_workspace_agent_server_client() -> None:
    workspace = Mock()
    response = Mock()
    workspace.client.post.return_value = response
    llm = LLM(model="openai/test-model", api_key=SecretStr("test-secret"))

    provision_llm_profile(workspace, profile_name="strong-profile", llm=llm)

    workspace.client.post.assert_called_once()
    path = workspace.client.post.call_args.args[0]
    payload = workspace.client.post.call_args.kwargs["json"]
    assert path == "/api/profiles/strong-profile"
    assert payload["llm"]["model"] == "openai/test-model"
    assert payload["llm"]["api_key"] == "test-secret"
    assert payload["include_secrets"] is True
    response.raise_for_status.assert_called_once_with()


def test_empty_profile_store_guard_allows_clean_agent_server() -> None:
    workspace = Mock()
    response = Mock()
    response.json.return_value = {"profiles": [], "active_profile": None}
    workspace.client.get.return_value = response

    assert_empty_llm_profile_store(workspace)

    workspace.client.get.assert_called_once_with("/api/profiles")
    response.raise_for_status.assert_called_once_with()


def test_empty_profile_store_guard_rejects_extra_model_choices() -> None:
    workspace = Mock()
    response = Mock()
    response.json.return_value = {
        "profiles": [{"name": "unexpected", "model": "openai/other"}],
        "active_profile": None,
    }
    workspace.client.get.return_value = response

    with pytest.raises(RuntimeError, match="unexpected"):
        assert_empty_llm_profile_store(workspace)


def test_switch_profile_name_contract() -> None:
    assert PROFILE_NAME_REGEX.fullmatch("alternate")
    assert not PROFILE_NAME_REGEX.fullmatch("strong/profile")
