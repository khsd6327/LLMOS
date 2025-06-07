from src.tedos.managers.settings import SettingsManager
from src.tedos.managers.chat_sessions import ChatSessionManager
from src.tedos.managers.model_manager import EnhancedModelManager
from src.tedos.managers.usage_tracker import UsageTracker
from src.tedos.managers.favorite_manager import FavoriteManager
from src.tedos.managers.spotify_manager import SpotifyManager


class AppContext:
    """Singleton-like application context providing access to managers."""

    def __init__(self) -> None:
        self.settings = SettingsManager()
        self.settings.ensure_paths_exist()
        self.usage_tracker = UsageTracker(self.settings.get("paths.usage_tracking"))
        self.model_manager = EnhancedModelManager(self.settings, self.usage_tracker)
        self.chat_manager = ChatSessionManager(self.settings.get("paths.chat_sessions"))
        self.favorite_manager = FavoriteManager(self.settings.get("paths.favorites"))
        self.spotify_manager = SpotifyManager(self.settings)


app_context = AppContext()


def get_app_context() -> AppContext:
    """Return shared application context."""
    return app_context
