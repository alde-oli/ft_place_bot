import sys

from client import FTPlaceAPI
from config import APIConfig
from core import ColorConfig, ColorPriority, ColorSet, ImageMonitor
from utils import ColorManager, parse_args, setup_logging


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
        ],
    )


def main():
    logger = setup_logging()
    args = parse_args()

    api_config = APIConfig(
        base_url="https://ftplace.42lwatch.ch",
        refresh_token=args.refresh_token,
        access_token=args.access_token,
        retry_attempts=3,
        check_interval=1.0,
    )

    try:
        api = FTPlaceAPI(api_config)

        logger.info("Checking connection...")
        profile = api.get_profile()
        if not profile:
            raise ValueError("Unable to retrieve user profile")
        logger.info("Connected as: %s", profile.username)  # Using %-formatting

        color_config = create_color_config()

        logger.info("Loading image: %s", args.img_path)  # Using %-formatting
        board_data = api.get_board()
        if not board_data:
            raise ValueError("Unable to retrieve board data")

        image_data = ColorManager.load_image(args.img_path)
        if image_data is None:
            raise ValueError("Unable to load image: %s" % args.img_path)

        target_colors = ColorManager.convert_to_ftplace_colors(image_data, board_data)
        logger.info("Image successfully converted")

        logger.info("Starting maintenance at position (%d, %d)", args.origin_x, args.origin_y)  # Using %-formatting
        monitor = ImageMonitor(api, api_config, color_config)
        monitor.monitor_and_maintain(target_colors=target_colors, origin_x=args.origin_x, origin_y=args.origin_y)

    except KeyboardInterrupt:
        logger.info("\nUser requested stop")
        sys.exit(0)
    except (OSError, ValueError) as e:  # Specific exceptions instead of blind catch
        logger.error("Critical error: %s", str(e))  # Using %-formatting
        sys.exit(1)


if __name__ == "__main__":
    main()
