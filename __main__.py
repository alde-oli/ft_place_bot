# ft_place/__main__.py
import argparse
import sys
import logging

from client_api import FTPlaceAPI
from color_config import ColorConfig, ColorPriority, ColorSet
from image_monitor import ImageMonitor
from utils import ColorManager
from config import APIConfig


def setup_logging() -> logging.Logger:
	logger = logging.getLogger()
	handler = logging.StreamHandler()
	formatter = logging.Formatter(
		'%(asctime)s - %(levelname)s - %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)
	handler.setFormatter(formatter)
	logger.addHandler(handler)
	logger.setLevel(logging.INFO)
	return logger


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description='FTPlace Image Maintainer')
	parser.add_argument('img_path', help='Path to the image to maintain')
	parser.add_argument('origin_x', type=int, help='X coordinate of the origin')
	parser.add_argument('origin_y', type=int, help='Y coordinate of the origin')
	parser.add_argument('access_token', help='Access token')
	parser.add_argument('refresh_token', help='Refresh token')
	return parser.parse_args()


def create_color_config() -> ColorConfig:
	return ColorConfig(
		priorities=[
			ColorPriority(priority_level=1, color_ids={4}),
			ColorPriority(priority_level=2, color_ids={1, 2}),
			ColorPriority(priority_level=3, color_ids={14}),
		],
		ignored_source_colors=set(),
		ignored_board_colors=set(),
		color_sets=[
			ColorSet(main_color=14, similar_colors={12, 13, 14}),
		]
	)


def main():
	logger = setup_logging()
	args = parse_args()
	
	api_config = APIConfig(
		base_url="https://ftplace.42lwatch.ch",
		refresh_token=args.refresh_token,
		access_token=args.access_token,
		retry_attempts=3,
		check_interval=1.0
	)

	try:
		api = FTPlaceAPI(api_config)
		
		logger.info("Checking connection...")
		profile = api.get_profile()
		if not profile:
			raise Exception("Unable to retrieve user profile")
		logger.info(f"Connected as: {profile.username}")

		color_config = create_color_config()
		
		logger.info(f"Loading image: {args.img_path}")
		board_data = api.get_board()
		if not board_data:
			raise Exception("Unable to retrieve board data")
		
		image_data = ColorManager.load_image(args.img_path)
		if image_data is None:
			raise Exception(f"Unable to load image: {args.img_path}")
		
		target_colors = ColorManager.convert_to_ftplace_colors(image_data, board_data)
		logger.info("Image successfully converted")

		logger.info(f"Starting maintenance at position ({args.origin_x}, {args.origin_y})")
		monitor = ImageMonitor(api, api_config, color_config)
		monitor.monitor_and_maintain(
			target_colors=target_colors,
			origin_x=args.origin_x,
			origin_y=args.origin_y
		)

	except KeyboardInterrupt:
		logger.info("\nUser requested stop")
		sys.exit(0)
	except Exception as e:
		logger.error(f"Critical error: {e}")
		sys.exit(1)

if __name__ == "__main__":
	main()