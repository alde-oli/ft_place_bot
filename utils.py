from typing import Tuple, Dict, Optional
import math
import numpy as np
from PIL import Image
from exceptions import FTPlaceError


class ColorManager:
    @staticmethod
    def get_color_distance(color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        return math.sqrt(sum((float(a) - float(b)) ** 2 for a, b in zip(color1, color2)))

    @staticmethod
    def find_closest_color(rgb: Tuple[int, int, int], board_data: Dict) -> int:
        min_distance = float('inf')
        closest_color_id = 1

        for color in board_data['colors']:
            ftplace_rgb = (color['red'], color['green'], color['blue'])
            distance = ColorManager.get_color_distance(rgb, ftplace_rgb)
            if distance < min_distance:
                min_distance = distance
                closest_color_id = color['id']

        return closest_color_id

    @staticmethod
    def load_image(image_path: str) -> Optional[np.ndarray]:
        try:
            with Image.open(image_path) as img:
                return np.array(img.convert('RGB'))
        except Exception as e:
            raise FTPlaceError(f"Failed to load image: {e}")

    @staticmethod
    def convert_to_ftplace_colors(image: np.ndarray, board_data: Dict) -> np.ndarray:
        height, width, _ = image.shape
        color_map = np.zeros((width, height), dtype=np.int32)
        
        for y in range(height):
            for x in range(width):
                rgb = tuple(map(int, image[y, x]))
                color_map[x][y] = ColorManager.find_closest_color(rgb, board_data)
                
        return color_map
