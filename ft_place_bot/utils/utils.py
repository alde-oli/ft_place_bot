import argparse
import logging
import math
from typing import Any, Dict, Optional, Tuple

import numpy as np
from numpy.typing import NDArray
from PIL import Image, UnidentifiedImageError

from ft_place_bot.core import FTPlaceError


class ColorManager:
    @staticmethod
    def get_color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(color1, color2)))

    @staticmethod
    def find_closest_color(rgb: Tuple[int, int, int], board_data: Dict[str, Any]) -> int:
        min_distance = float("inf")
        closest_color_id = 1

        for color in board_data["colors"]:
            ftplace_rgb = (color["red"], color["green"], color["blue"])
            distance = ColorManager.get_color_distance(rgb, ftplace_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_color_id = color["id"]

        return closest_color_id

    @staticmethod
    def load_image(image_path: str) -> Optional[NDArray[np.uint8]]:
        try:
            with Image.open(image_path) as img:
                return np.array(img.convert("RGB"))
        except (OSError, UnidentifiedImageError, ValueError) as err:
            raise FTPlaceError("Failed to load image") from err

    @staticmethod
    def convert_to_ftplace_colors(image: NDArray[np.uint8], board_data: Dict[str, Any]) -> NDArray[np.int32]:
        height, width, _ = image.shape
        color_map = np.zeros((width, height), dtype=np.int32)

        for y in range(height):
            for x in range(width):
                rgb: Tuple[int, int, int] = (int(image[y, x][0]), int(image[y, x][1]), int(image[y, x][2]))
                color_map[x][y] = ColorManager.find_closest_color(rgb, board_data)

        return color_map


def setup_logging() -> logging.Logger:
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="FTPlace Image Maintainer")
    parser.add_argument("img_path", help="Path to the image to maintain")
    parser.add_argument("origin_x", type=int, help="X coordinate of the origin")
    parser.add_argument("origin_y", type=int, help="Y coordinate of the origin")
    parser.add_argument("access_token", help="Access token")
    parser.add_argument("refresh_token", help="Refresh token")
    return parser.parse_args()
