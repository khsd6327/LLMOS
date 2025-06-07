import asyncio
from types import SimpleNamespace, ModuleType
from datetime import datetime
import sys
import types

import pytest

# Stub external dependencies before importing project modules
sys.modules.setdefault("openai", types.SimpleNamespace(OpenAI=lambda *a, **k: object()))
sys.modules.setdefault("anthropic", ModuleType("anthropic"))
google_stub = ModuleType("google")
google_stub.generativeai = types.SimpleNamespace(
    GenerativeModel=lambda *a, **k: object(), configure=lambda *a, **k: None
)
sys.modules.setdefault("google", google_stub)
sys.modules.setdefault("PIL", ModuleType("PIL"))
sys.modules.setdefault("PIL.Image", ModuleType("PIL.Image"))
spotipy_stub = ModuleType("spotipy")
spotipy_stub.oauth2 = ModuleType("spotipy.oauth2")
spotipy_stub.oauth2.SpotifyOAuth = object
sys.modules.setdefault("spotipy", spotipy_stub)
sys.modules.setdefault("spotipy.oauth2", spotipy_stub.oauth2)
class DummyState(dict):
    def __getattr__(self, item):
        return self.get(item)

    def __setattr__(self, item, value):
        self[item] = value

streamlit_stub = ModuleType("streamlit")
streamlit_stub.session_state = DummyState()
sys.modules.setdefault("streamlit", streamlit_stub)

from backend.main import handle_chat_message, ChatMessageRequest
from src.tedos.managers.model_management.response_manager import ResponseManager
from src.tedos.models.data_models import ChatSession, ModelConfig
from src.tedos.models.enums import ModelProvider


class FakeSettings:
    def __init__(self):
        self.data = {"ui": {"selected_provider": "OpenAI"}}

    def get(self, path, default=None):
        current = self.data
        for part in path.split("."):
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current

    def get_default_model_for_provider(self, provider_name):
        return {"OpenAI": "gpt-4.1-mini"}.get(provider_name, "")


class FakeChatManager:
    def __init__(self, session):
        self.sessions = {session.id: session}

    def get_session(self, sid):
        return self.sessions.get(sid)

    def update_session(self, session):
        self.sessions[session.id] = session


class FakeModelManager:
    def __init__(self):
        self.last_provider = None
        self.last_model = None

    def stream_generate(self, messages, provider_display_name=None, model_id_key=None, **kwargs):
        self.last_provider = provider_display_name
        self.last_model = model_id_key
        async def gen():
            yield "done", None
        return gen()


def test_handle_chat_message_uses_default_model():
    session = ChatSession(id="s1", title="t", messages=[], created_at=datetime.now(), updated_at=datetime.now(), metadata={})
    context = SimpleNamespace(
        settings=FakeSettings(),
        chat_manager=FakeChatManager(session),
        model_manager=FakeModelManager()
    )

    request = ChatMessageRequest(prompt="hi", model_provider="OpenAI")
    response = asyncio.run(handle_chat_message("s1", request, context))

    async def consume(resp):
        async for _ in resp.body_iterator:
            break

    asyncio.run(consume(response))

    assert context.model_manager.last_provider == "OpenAI"
    assert context.model_manager.last_model == "gpt-4.1-mini"


def test_response_manager_stream_uses_default(monkeypatch):
    settings = FakeSettings()

    def fake_get_active_config(provider_display_name, model_id_key):
        cfg = ModelConfig(
            provider=ModelProvider.OPENAI,
            model_name="dummy",
            display_name="Dummy",
            max_tokens=10,
            supports_streaming=False,
            supports_functions=False,
        )
        return ModelProvider.OPENAI, cfg, object()

    rm = ResponseManager(interface_manager=object(), settings_manager=settings, usage_tracker=None, config_resolver_callback=fake_get_active_config)

    captured = {}
    def fake_generate(messages, provider_display_name=None, model_id_key=None, **kwargs):
        captured["provider"] = provider_display_name
        captured["model"] = model_id_key
        return "resp", None

    monkeypatch.setattr(rm, "generate", fake_generate)

    list(rm.stream_generate([], provider_display_name="OpenAI", model_id_key=None))

    assert captured["provider"] == "OpenAI"
    assert captured["model"] == "gpt-4.1-mini"
