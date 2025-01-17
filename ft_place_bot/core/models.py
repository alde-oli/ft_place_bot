from dataclasses import dataclass
from typing import List


@dataclass
class Pixel:
    x: int
    y: int
    color: int

    def to_dict(self) -> dict:
        return {
            "x": int(self.x),
            "y": int(self.y),
            "color": int(self.color)
        }


@dataclass
class UserProfile:
    timers: List[str]
    pixel_buffer: int
    pixel_timer: int
    id: int
    username: str
    is_admin: bool
    is_banned: bool
    iat: int
    exp: int

    @classmethod
    def from_api_response(cls, data: dict) -> 'UserProfile':
        user_infos = data.get('userInfos', {})
        return cls(
            timers=user_infos.get('timers', []),
            pixel_buffer=user_infos.get('pixel_buffer', 0),
            pixel_timer=user_infos.get('pixel_timer', 0),
            id=user_infos.get('id', 0),
            username=user_infos.get('username', ''),
            is_admin=user_infos.get('soft_is_admin', False),
            is_banned=user_infos.get('soft_is_banned', False),
            iat=user_infos.get('iat', 0),
            exp=user_infos.get('exp', 0)
        )
