from types import SimpleNamespace

from fastapi.testclient import TestClient
from pydantic import SecretStr

from openhands.agent_server.api import create_app
from openhands.agent_server.config import Config
from openhands.sdk import LLM
from openhands.sdk.llm import llm_profile_store

from benchmarks.swebench.run_infer import (
    assert_empty_llm_profile_store,
    provision_llm_profile,
)


def test_v7_provisions_profile_against_real_agent_server(tmp_path, monkeypatch):
    # LLMProfileStore._DEFAULT_PROFILE_DIR is resolved at import time in the
    # pinned SDK, so isolate it explicitly rather than relying on
    # OH_PERSISTENCE_DIR after imports.
    profile_dir = tmp_path / "profiles"
    profile_dir.mkdir()

    monkeypatch.setattr(
        llm_profile_store,
        "_DEFAULT_PROFILE_DIR",
        profile_dir,
    )

    app = create_app(Config(session_api_keys=[]))

    with TestClient(app) as client:
        workspace = SimpleNamespace(client=client)

        # Scientific contamination guard: server must start with no profiles.
        assert_empty_llm_profile_store(workspace)

        alternate = LLM(
            model="dummy/model-b",
            usage_id="profile:alternate",
            api_key=SecretStr("dummy-secret"),
            temperature=0.0,
        )

        provision_llm_profile(
            workspace,
            profile_name="alternate",
            llm=alternate,
        )

        response = client.get("/api/profiles")
        response.raise_for_status()

        payload = response.json()

        assert [p["name"] for p in payload["profiles"]] == ["alternate"]

        # Prove it was persisted into the isolated store, not ~/.openhands.
        stored = llm_profile_store.LLMProfileStore(
            base_dir=profile_dir
        ).load("alternate")

        assert stored.model == "dummy/model-b"
        assert stored.usage_id == "profile:alternate"
        assert stored.api_key is not None
        assert stored.api_key.get_secret_value() == "dummy-secret"
