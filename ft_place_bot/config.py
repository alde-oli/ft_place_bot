from dataclasses import dataclass
from enum import Enum


class ColorID(Enum):
    WHITE = 1
    LIGHTGRAY = 2
    DARKGRAY = 3
    BLACK = 4
    PINK = 5
    DARKRED = 18
    RED = 6
    ORANGE = 7
    BROWN = 8
    BEIGE = 17
    YELLOW = 9
    LIME = 10
    GREEN = 11
    CYAN = 12
    BLUE = 13
    INDIGO = 14
    MAGENTA = 15
    PURPLE = 16


class APIEndpoints(Enum):
    PROFILE = "/api/profile"
    BOARD = "/api/get"
    SET_PIXEL = "/api/set"


class HTTPStatus(Enum):
    TOO_EARLY = 425
    TOKEN_EXPIRED = 426
    SUCCESS_200 = 200
    SUCCESS_201 = 201
    SUCCESS_204 = 204

    @classmethod
    def is_success(cls, status_code):
        return status_code in {
            cls.SUCCESS_200.value,
            cls.SUCCESS_201.value,
            cls.SUCCESS_204.value,
        }


@dataclass
class APIConfig:
    base_url: str
    refresh_token: str
    access_token: str
    retry_attempts: int = 3
    check_interval: float = 1.0


from pathlib import Path
from typing import List, Optional, Set

from pydantic import BaseModel


class UserConfiguration(BaseModel):
    access_token: str
    refresh_token: str
    last_image_path: Optional[str] = None
    last_origin_x: Optional[int] = None
    last_origin_y: Optional[int] = None
    color_priorities: List[dict] = []
    ignored_colors: Set[int] = set()
    similar_colors: List[dict] = []

    @classmethod
    def load(cls) -> "UserConfiguration":
        config_path = Path.home() / ".ft_place_bot_config.json"
        if config_path.exists():
            return cls.parse_raw(config_path.read_text())
        return cls(access_token=None, refresh_token=None)

    def save(self):
        config_path = Path.home() / ".ft_place_bot_config.json"
        config_path.write_text(self.json())
