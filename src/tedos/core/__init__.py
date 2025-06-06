# ted-os-project/src/tedos/core/__init__.py
"""
Ted OS 핵심 모듈
"""

from .config import *
=======
from .config import *

>>>>>>> fix/remove-app-imports
__all__ = [
    # config 모듈의 모든 상수들
    "APP_VERSION",
    "APP_NAME",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "MAX_HISTORY_LENGTH",
]