import importlib.util
import types
from pathlib import Path
from datetime import datetime
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]
DM_PATH = ROOT / "backend" / "models" / "data_models.py"

sys.modules.setdefault("backend", types.ModuleType("backend"))
sys.modules["backend"].__path__ = [str(ROOT / "backend")]
sys.modules.setdefault("backend.models", types.ModuleType("backend.models"))
sys.modules["backend.models"].__path__ = [str(ROOT / "backend" / "models")]

spec = importlib.util.spec_from_file_location("backend.models.data_models", DM_PATH)
data_models = importlib.util.module_from_spec(spec)
sys.modules["backend.models.data_models"] = data_models
spec.loader.exec_module(data_models)
ChatSession = data_models.ChatSession


def test_chat_session_is_pinned_roundtrip():
    session = ChatSession(
        id="123",
        title="Test",
        messages=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={},
        is_pinned=True,
    )

    data = session.to_dict()
    assert data["is_pinned"] is True

    recovered = ChatSession.from_dict(data)
    assert recovered.is_pinned is True
    assert recovered.id == session.id

