import importlib
import sys
import types
from pathlib import Path
from datetime import datetime

# Helper loader to import modules without executing heavy package __init__
TEST_ROOT = Path(__file__).resolve().parents[1]
TEDOS_PATH = TEST_ROOT / "backend"

if "backend" not in sys.modules:
    pkg = types.ModuleType("backend")
    pkg.__path__ = [str(TEDOS_PATH)]
    sys.modules["backend"] = pkg

helpers = importlib.import_module("backend.utils.helpers")
models = importlib.import_module("backend.models.data_models")


def test_sanitize_filename_invalid_chars():
    raw = 'test<>:"/\\|?*.txt'
    assert helpers.sanitize_filename(raw) == 'test_________.txt'


def test_sanitize_filename_whitespace_and_dots():
    raw = '  bad .. file...name  '
    assert helpers.sanitize_filename(raw) == 'bad . file.name'


def test_truncate_text_noop():
    text = 'hello'
    assert helpers.truncate_text(text, max_length=10) == text


def test_truncate_text_truncates():
    text = 'hello world'
    assert helpers.truncate_text(text, max_length=8) == 'hello...'


def test_chat_session_serialization_roundtrip():
    now = datetime.now()
    original = models.ChatSession(
        id='1',
        title='t',
        messages=[{"role": "user", "content": "hi"}],
        created_at=now,
        updated_at=now,
        metadata={'a': 1},
        is_pinned=True,
    )
    data = original.to_dict()
    restored = models.ChatSession.from_dict(data)
    assert restored == original


def test_app_state_serialization_roundtrip():
    now = datetime.now()
    state = models.AppState(
        current_session_id='s1',
        current_page='chat',
        is_initialized=True,
        last_activity=now,
    )
    data = state.to_dict()
    restored = models.AppState.from_dict(data)
    assert restored == state


def test_spotify_track_serialization_roundtrip():
    track = models.SpotifyTrack(
        id='t1',
        name='Song',
        artists='Artist',
        duration_ms=210000,
        album_name='Album',
        release_date='2024-01-01',
        popularity=50,
    )
    data = track.to_dict()
    restored = models.SpotifyTrack.from_dict(data)
    assert restored == track


def test_extract_urls_simple():
    text = "Visit https://example.com for docs"
    assert helpers.extract_urls(text) == ["https://example.com"]


def test_extract_urls_multiple_and_punctuation():
    text = "Links: https://a.com, http://b.org/path?x=1#y!"
    urls = helpers.extract_urls(text)
    assert urls == ["https://a.com,", "http://b.org/path?x=1#y!"]
