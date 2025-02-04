import sys
from typing import List, Set

from ft_place_bot.client.client_api import FTPlaceAPI
from ft_place_bot.config import APIConfig
from ft_place_bot.core import ColorConfig, ColorPriority, ColorSet, ImageMonitor
from ft_place_bot.interface import Interface, PriorityConfig, SimilarColorConfig
from ft_place_bot.utils import ColorManager, setup_logging


def create_color_config(
    priorities: List[PriorityConfig],
    ignored_source_colors: Set[int],
    ignored_board_colors: Set[int],
    similar_colors: List[SimilarColorConfig],
) -> ColorConfig:
    return ColorConfig(
        priorities=[
            ColorPriority(priority_level=p["priority_level"], color_ids=set(p["color_ids"])) for p in priorities
        ],
        ignored_source_colors=ignored_source_colors,
        ignored_board_colors=ignored_board_colors,
        color_sets=[
            ColorSet(main_color=s["main_color"], similar_colors=set(s["similar_colors"])) for s in similar_colors
        ],
    )


def main() -> None:
    logger = setup_logging()

    access_token, refresh_token = Interface.get_tokens()
    img_path = Interface.get_image_path()
    origin_x, origin_y = Interface.get_origin()
    priorities, ignored_source_colors, ignored_board_colors, similar_colors = Interface.configure_colors()

    api_config = APIConfig(
        base_url="https://ftplace.42lwatch.ch",
        refresh_token=refresh_token,
        access_token=access_token,
        retry_attempts=3,
        check_interval=1.0,
    )

    try:
        api = FTPlaceAPI(api_config)

        logger.info("Checking connection...")
        profile = api.get_profile()
        if not profile:
            raise ValueError("Unable to retrieve user profile")
        logger.info("Connected as: %s", profile.username)

        color_config = create_color_config(priorities, ignored_source_colors, ignored_board_colors, similar_colors)

        logger.info("Loading image: %s", img_path)
        board_data = api.get_board()
        if not board_data:
            raise ValueError("Unable to retrieve board data")

        image_data = ColorManager.load_image(img_path)
        if image_data is None:
            raise ValueError("Unable to load image: %s" % img_path)

        target_colors = ColorManager.convert_to_ftplace_colors(image_data, board_data)
        logger.info("Image successfully converted")

        logger.info("Starting maintenance at position (%d, %d)", origin_x, origin_y)
        monitor = ImageMonitor(api, api_config, color_config)
        monitor.monitor_and_maintain(target_colors=target_colors, origin_x=origin_x, origin_y=origin_y)

    except KeyboardInterrupt:
        logger.info("\nUser requested stop")
        sys.exit(0)
    except (OSError, ValueError) as e:
        logger.error("Critical error: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
