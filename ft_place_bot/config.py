from dataclasses import dataclass
from enum import Enum


class ColorID(Enum):
    WHITE = 1
    LIGHTGRAY = 2
    DARKGRAY = 3
    BLACK = 4
    PINK = 5
    RED = 6
    ORANGE = 7
    BROWN = 8
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
