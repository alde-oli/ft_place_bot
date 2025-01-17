from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

class ColorID(Enum):
    TRANSPARENT = 14

class APIEndpoints(Enum):
    PROFILE = "/api/profile"
    BOARD = "/api/get"
    SET_PIXEL = "/api/set"

class HTTPStatus(Enum):
    TOO_EARLY = 425
    TOKEN_EXPIRED = 426
    SUCCESS = 200

@dataclass
class APIConfig:
    base_url: str
    refresh_token: str
    access_token: str
    retry_attempts: int = 3
    check_interval: float = 1.0