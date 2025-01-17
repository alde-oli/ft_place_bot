# color_config.py
from dataclasses import dataclass
from typing import List, Set, Optional

@dataclass
class ColorSet:
	"""Represents a set of similar colors"""
	main_color: int
	similar_colors: Set[int]


@dataclass
class ColorPriority:
	"""Config for color priority"""
	priority_level: int
	color_ids: Set[int]


@dataclass
class ColorConfig:
	"""Global color configuration"""
	priorities: List[ColorPriority]
	ignored_source_colors: Set[int]
	ignored_board_colors: Set[int]
	color_sets: List[ColorSet]

	def get_priority_level(self, color_id: int) -> Optional[int]:
		"""Returns the priority level of a color"""
		for priority in self.priorities:
			if color_id in priority.color_ids:
				return priority.priority_level
		return None

	def get_main_color(self, color_id: int) -> int:
		"""Returns the main color of a set of similar colors"""
		for color_set in self.color_sets:
			if color_id in color_set.similar_colors:
				return color_set.main_color
		return color_id

	def should_ignore_source(self, color_id: int) -> bool:
		"""Checks if a color should be ignored in the source"""
		return color_id in self.ignored_source_colors

	def should_ignore_board(self, color_id: int) -> bool:
		"""Checks if a color should be ignored in the board"""
		return color_id in self.ignored_board_colors


# Example configuration:
if __name__ == "__main__":
	example_config = ColorConfig(
		priorities=[
			ColorPriority(priority_level=1, color_ids={1, 2, 3}),  # Critical colors
			ColorPriority(priority_level=2, color_ids={4, 5, 6}),  # Important colors
			ColorPriority(priority_level=3, color_ids={7, 8, 9}),  # Normal colors
		],
		ignored_source_colors={14},
		ignored_board_colors={0},
		color_sets=[
			ColorSet(main_color=2, similar_colors={12, 13, 14}),  # Blue shades
		]
	)
	print(example_config.get_priority_level(4))  # Output: 2