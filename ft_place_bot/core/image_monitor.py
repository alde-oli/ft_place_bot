import logging
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
from requests.exceptions import RequestException

from ft_place_bot.config import HTTPStatus
from ft_place_bot.core.color_config import ColorConfig
from ft_place_bot.core.exceptions import TokenError


@dataclass
class PixelToFix:
    x: int
    y: int
    current_color: int
    target_color: int
    priority: int


class ImageMonitor:
    def __init__(self, api: Any, config: Any, color_config: ColorConfig) -> None:
        self.api = api
        self.config = config
        self.color_config = color_config
        self.logger = logging.getLogger(__name__)

    def _convert_board_color(self, color_id: int) -> int:
        """Converts a board color considering sets of similar colors"""
        if self.color_config.should_ignore_board(color_id):
            return -1
        return self.color_config.get_main_color(color_id)

    def _convert_target_color(self, color_id: int) -> int:
        """Converts a target color considering sets of similar colors"""
        if self.color_config.should_ignore_source(color_id):
            return -1
        return self.color_config.get_main_color(color_id)

    def get_image_stats(
        self, board: np.ndarray[Any, Any], target_colors: np.ndarray[Any, Any], origin_x: int, origin_y: int
    ) -> Dict[str, Any]:
        image_width, image_height = target_colors.shape
        correct_pixels = incorrect_pixels = total_countable_pixels = 0

        for x in range(image_width):
            for y in range(image_height):
                target_color = self._convert_target_color(target_colors[x][y])
                if target_color == -1:
                    continue
                board_x, board_y = origin_x + x, origin_y + y
                if 0 <= board_x < board.shape[0] and 0 <= board_y < board.shape[1]:
                    board_color = self._convert_board_color(board[board_x][board_y])
                    if board_color == -1:
                        continue

                    total_countable_pixels += 1
                    if board_color == target_color:
                        correct_pixels += 1
                    else:
                        incorrect_pixels += 1

        completion_percentage = (correct_pixels / total_countable_pixels * 100) if total_countable_pixels > 0 else 0

        return {
            "total_pixels": total_countable_pixels,
            "correct_pixels": correct_pixels,
            "incorrect_pixels": incorrect_pixels,
            "completion_percentage": round(completion_percentage, 2),
        }

    def _get_pixels_to_fix(
        self, board: np.ndarray[Any, Any], target_colors: np.ndarray[Any, Any], origin_x: int, origin_y: int
    ) -> List[PixelToFix]:
        image_width, image_height = target_colors.shape
        pixels_to_fix = []

        for x in range(image_width):
            for y in range(image_height):
                target_color = target_colors[x][y]
                if self.color_config.should_ignore_source(target_color):
                    continue
                board_x, board_y = origin_x + x, origin_y + y
                if not (0 <= board_x < board.shape[0] and 0 <= board_y < board.shape[1]):
                    continue
                board_color = board[board_x][board_y]
                if self.color_config.should_ignore_board(board_color):
                    continue

                target_main_color = self.color_config.get_main_color(target_color)
                board_main_color = self.color_config.get_main_color(board_color)

                if board_main_color != target_main_color:
                    priority = self.color_config.get_priority_level(target_color) or 999
                    pixels_to_fix.append(
                        PixelToFix(
                            x=board_x,
                            y=board_y,
                            current_color=board_color,
                            target_color=target_color,
                            priority=priority,
                        )
                    )
        # Sort by priority
        pixels_to_fix.sort(key=lambda pixel: (pixel.priority, secrets.randbelow(1000000)))
        return pixels_to_fix

    def _handle_pixel_placement(self, pixel: PixelToFix) -> bool:
        try:
            response = self.api.session.post(
                f"{self.api.config.base_url}/api/set",
                json={"x": int(pixel.x), "y": int(pixel.y), "color": int(pixel.target_color)},
            )
            # Handle different response cases
            if response.status_code == HTTPStatus.TOO_EARLY.value:  # Too early
                wait_time: float = 0.0
                user = self.api.get_profile()
                if not user:
                    error_data = response.json()
                    if "timers" in error_data:
                        next_time = datetime.fromisoformat(error_data["timers"][0].replace("Z", "+00:00"))
                        wait_time = (next_time - datetime.now(timezone.utc)).total_seconds()
                else:
                    next_time = min([datetime.fromisoformat(timer.replace("Z", "+00:00")) for timer in user.timers])
                    wait_time = (next_time - datetime.now(timezone.utc)).total_seconds()

                if wait_time > 0:
                    next_time_str = next_time.astimezone().strftime("%H:%M:%S")
                    self.logger.info("Next pixel available in %.1f seconds | %s", wait_time, next_time_str)
                    time.sleep(wait_time + 1)
                else:
                    time.sleep(5)
                return False

            try:
                response, needs_retry = self.api.handle_response(response)
                # If needs_retry is True, try the request again
                if needs_retry:
                    response = self.api.session.post(
                        f"{self.api.config.base_url}/api/set",
                        json={"x": int(pixel.x), "y": int(pixel.y), "color": int(pixel.target_color)},
                    )
                    response, _ = self.api.handle_response(response)  # Handle response again if needed

                if HTTPStatus.is_success(response.status_code):  # Success
                    self.logger.info("Pixel successfully placed at (%d, %d)", pixel.x, pixel.y)
                    return True
                self.logger.error("Unexpected error: %d - %s", response.status_code, response.text)
                time.sleep(5)
                return False

            except TokenError as e:
                self.logger.error("Token error: %s", str(e))
                time.sleep(5)
                return False

        except (OSError, RequestException, ValueError) as e:
            self.logger.error("Error placing pixel: %s", str(e))
            return False

    def monitor_and_maintain(self, target_colors: np.ndarray[Any, Any], origin_x: int, origin_y: int) -> None:
        max_board_retries = 3
        while True:
            try:
                board_data = self.api.get_board()
                if not board_data:
                    if max_board_retries > 0:
                        max_board_retries -= 1
                        continue
                    raise ValueError("Unable to get the board")
                if "board" not in board_data:
                    if max_board_retries > 0:
                        max_board_retries -= 1
                        continue
                    raise ValueError("Invalid board data")
                max_board_retries = 3

                board = np.array([[cell["color_id"] for cell in row] for row in board_data["board"]])
                # Get and display stats
                stats = self.get_image_stats(board, target_colors, origin_x, origin_y)
                self.logger.info(
                    "Image stats: %d/%d correct pixels (%.2f%% completed), %d pixels to fix",
                    stats["correct_pixels"],
                    stats["total_pixels"],
                    stats["completion_percentage"],
                    stats["incorrect_pixels"],
                )
                # Get pixels to fix
                pixels_to_fix = self._get_pixels_to_fix(board, target_colors, origin_x, origin_y)
                if not pixels_to_fix:
                    self.logger.info("Image correct, checking again in 5 seconds...")
                    time.sleep(5)
                    continue
                # Process the highest priority pixel
                self._handle_pixel_placement(pixels_to_fix[0])

            except (OSError, RequestException, ValueError) as e:
                self.logger.error("Error in main loop: %s", str(e))
                time.sleep(self.config.check_interval)
