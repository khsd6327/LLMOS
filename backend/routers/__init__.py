from .chat import router as chat_router
from .favorites import router as favorites_router
from .settings import router as settings_router
from .status import router as status_router

all_routers = [chat_router, favorites_router, settings_router, status_router]
__all__ = ["all_routers"]
