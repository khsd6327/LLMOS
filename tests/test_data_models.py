import datetime
import sys
import types
from pathlib import Path
import importlib

# Set up minimal package structure to load data_models without executing tedos.__init__
package_path = Path(__file__).resolve().parents[1] / "src/tedos"
package = types.ModuleType("tedos")
package.__path__ = [str(package_path)]
sys.modules["tedos"] = package

# Now import the module normally under the package
data_models = importlib.import_module("tedos.models.data_models")
AppState = data_models.AppState


def test_app_state_round_trip_with_last_activity():
    orig = AppState(
        current_session_id="123",
        current_page="settings",
        is_initialized=True,
        last_activity=datetime.datetime(2024, 5, 17, 12, 0, 0)
    )
    data = orig.to_dict()
    assert set(data.keys()) == {"current_session_id", "current_page", "is_initialized", "last_activity"}
    assert data["last_activity"] == orig.last_activity.isoformat()
    new = AppState.from_dict(data)
    assert new == orig


def test_app_state_round_trip_without_last_activity():
    orig = AppState(
        current_session_id="789",
        current_page="chat",
        is_initialized=False,
        last_activity=None
    )
    data = orig.to_dict()
    assert data["last_activity"] is None
    new = AppState.from_dict(data)
    assert new == orig
