# image_monitor.py
import numpy as np
import logging
from typing import List
import time
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class PixelToFix:
	x: int
	y: int
	current_color: int
	target_color: int
	priority: int


class ImageMonitor:
	
	def __init__(self, api, config, color_config):
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


	def get_image_stats(self, board: np.ndarray, target_colors: np.ndarray, 
					   origin_x: int, origin_y: int) -> dict:
		"""Calculates image statistics considering the color configuration"""
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
			"completion_percentage": round(completion_percentage, 2)
		}

	def _get_pixels_to_fix(self, board: np.ndarray, target_colors: np.ndarray,
						  origin_x: int, origin_y: int) -> List[PixelToFix]:
		"""
		Identifies pixels to fix considering priorities and color rules
		"""
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
					pixels_to_fix.append(PixelToFix(
						x=board_x,
						y=board_y,
						current_color=board_color,
						target_color=target_color,
						priority=priority
					))
		# Sort by priority
		return sorted(pixels_to_fix, key=lambda p: p.priority)


	def _handle_pixel_placement(self, pixel: PixelToFix) -> bool:
		"""Handles pixel placement with retry and error management"""
		try:
			response = self.api.session.post(
				f"{self.api.config.base_url}/api/set",
				json={
					"x": int(pixel.x),
					"y": int(pixel.y),
					"color": int(pixel.target_color)
				}
			)
			# Handle different response cases
			if response.status_code == 425:  # Too early
				error_data = response.json()
				if "timers" in error_data:
					next_time = datetime.fromisoformat(error_data["timers"][0].replace('Z', '+00:00'))
					wait_time = (next_time - datetime.now(timezone.utc)).total_seconds()
					if wait_time > 0:
						self.logger.info(f"Next pixel available in {wait_time:.1f} seconds")
						time.sleep(wait_time + 1)
					else:
						time.sleep(5)
				return False   
			elif response.status_code == 426:  # Token expired
				response = self.api._handle_response(response)
				if response.status_code == 426:
					raise Exception("Both tokens are expired")
				return False    
			elif response.status_code == 200:
				self.logger.info(f"Pixel successfully placed at ({pixel.x}, {pixel.y})")
				return True  
			else:
				self.logger.error(f"Unexpected error: {response.status_code} - {response.text}")
				time.sleep(5)
				return False

		except Exception as e:
			self.logger.error(f"Error placing pixel: {e}")
			return False


	def monitor_and_maintain(self, target_colors: np.ndarray, origin_x: int, origin_y: int):
		"""Monitors and maintains the image on the board"""
		while True:
			try:
				board_data = self.api.get_board()
				if not board_data:
					raise Exception("Unable to get the board")

				board = np.array([[cell['color_id'] for cell in row] for row in board_data['board']])
				# Get and display stats
				stats = self.get_image_stats(board, target_colors, origin_x, origin_y)
				self.logger.info(
					f"Image stats: "
					f"{stats['correct_pixels']}/{stats['total_pixels']} correct pixels "
					f"({stats['completion_percentage']}% completed), "
					f"{stats['incorrect_pixels']} pixels to fix"
				)
				# Get pixels to fix
				pixels_to_fix = self._get_pixels_to_fix(board, target_colors, origin_x, origin_y)
				if not pixels_to_fix:
					self.logger.info("Image correct, checking again in 5 seconds...")
					time.sleep(5)
					continue
				# Process the highest priority pixel
				self.logger.info(f"Pixels to fix: {len(pixels_to_fix)}")
				self._handle_pixel_placement(pixels_to_fix[0])

			except Exception as e:
				self.logger.error(f"Error in main loop: {e}")
				time.sleep(self.config.check_interval)