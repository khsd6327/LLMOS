import sys, types
import pytest

@pytest.fixture(autouse=True)
def stub_external_modules():
    # Provide minimal stubs for optional external dependencies
    sys.modules.setdefault('openai', types.SimpleNamespace(OpenAI=lambda *a, **k: object()))
    sys.modules.setdefault('anthropic', types.ModuleType('anthropic'))
    google_mod = types.ModuleType('google')
    google_mod.generativeai = types.SimpleNamespace(GenerativeModel=lambda *a, **k: object(), configure=lambda *a, **k: None)
    sys.modules.setdefault('google', google_mod)
    yield
