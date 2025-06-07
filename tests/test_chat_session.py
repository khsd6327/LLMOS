import importlib.util
import types
from pathlib import Path
from datetime import datetime
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1] / "src"
DM_PATH = ROOT / "tedos" / "models" / "data_models.py"

sys.modules.setdefault("tedos", types.ModuleType("tedos"))
sys.modules["tedos"].__path__ = [str(ROOT / "tedos")]
sys.modules.setdefault("tedos.models", types.ModuleType("tedos.models"))
sys.modules["tedos.models"].__path__ = [str(ROOT / "tedos" / "models")]

spec = importlib.util.spec_from_file_location("tedos.models.data_models", DM_PATH)
data_models = importlib.util.module_from_spec(spec)
sys.modules["tedos.models.data_models"] = data_models
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

