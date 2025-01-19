from pathlib import Path
from typing import Dict, List, Set, Tuple, TypedDict, cast

import questionary

from ft_place_bot.config import ColorID, UserConfiguration


class PriorityConfig(TypedDict):
    priority_level: int
    color_ids: List[int]


class SimilarColorConfig(TypedDict):
    main_color: int
    similar_colors: List[int]


class Interface:
    @staticmethod
    def get_tokens() -> Tuple[str, str]:
        config = UserConfiguration.load()
        if config.access_token is not None and config.refresh_token is not None:
            use_saved = questionary.confirm("Use saved tokens?", default=True).ask()
            if use_saved:
                # Type narrowing through runtime check
                saved_access = config.access_token
                saved_refresh = config.refresh_token
                if saved_access is None or saved_refresh is None:
                    raise ValueError("Saved tokens unexpectedly None")
                return saved_access, saved_refresh
        access_token = cast(str, questionary.text("Access Token:").ask())
        refresh_token = cast(str, questionary.text("Refresh Token:").ask())
        config.access_token = access_token
        config.refresh_token = refresh_token
        config.save()
        return access_token, refresh_token

    @staticmethod
    def get_image_path() -> str:
        config = UserConfiguration.load()
        if config.last_image_path:
            use_last = questionary.confirm(f"Use the last image ({config.last_image_path})?", default=True).ask()
            if use_last:
                return config.last_image_path
        image_path = cast(str, questionary.path("Image path:", validate=lambda x: Path(x).exists()).ask())
        config.last_image_path = image_path
        config.save()
        return image_path

    @staticmethod
    def get_origin() -> Tuple[int, int]:
        config = UserConfiguration.load()
        if config.last_origin_x is not None and config.last_origin_y is not None:
            use_last = questionary.confirm(
                f"Use the last position ({config.last_origin_x}, {config.last_origin_y})?", default=True
            ).ask()
            if use_last:
                return config.last_origin_x, config.last_origin_y
        origin_x = cast(str, questionary.text("Position X:", validate=lambda x: x.isdigit()).ask())
        origin_y = cast(str, questionary.text("Position Y:", validate=lambda x: x.isdigit()).ask())
        config.last_origin_x = int(origin_x)
        config.last_origin_y = int(origin_y)
        config.save()
        return int(origin_x), int(origin_y)

    @staticmethod
    def configure_colors() -> Tuple[List[PriorityConfig], Set[int], Set[int], List[SimilarColorConfig]]:
        config = UserConfiguration.load()
        if config.color_priorities:
            use_saved = questionary.confirm("Use saved color configuration?", default=True).ask()
            if use_saved:
                return (
                    cast(List[PriorityConfig], config.color_priorities),
                    config.ignored_source_colors,
                    config.ignored_board_colors,
                    cast(List[SimilarColorConfig], config.similar_colors),
                )
        # Interface to configure priorities
        priorities: List[PriorityConfig] = []
        while questionary.confirm("Add a priority?").ask():
            level = cast(str, questionary.text("Priority level (1-3):", validate=lambda x: x in ["1", "2", "3"]).ask())
            colors = cast(
                List[str],
                questionary.checkbox("Select colors:", choices=[f"{c.name} ({c.value})" for c in ColorID]).ask(),
            )
            color_ids = {int(c.split("(")[1][:-1]) for c in colors}
            priorities.append({"priority_level": int(level), "color_ids": list(color_ids)})
        # Interface for ignored colors
        ignored_source = cast(
            List[str],
            questionary.checkbox(
                "Select colors to ignore on the source image:", choices=[f"{c.name} ({c.value})" for c in ColorID]
            ).ask(),
        )
        ignored_source_colors: Set[int] = {int(c.split("(")[1][:-1]) for c in ignored_source}
        ignored_board = cast(
            List[str],
            questionary.checkbox(
                "Select colors to ignore on the board:", choices=[f"{c.name} ({c.value})" for c in ColorID]
            ).ask(),
        )
        ignored_board_colors: Set[int] = {int(c.split("(")[1][:-1]) for c in ignored_board}
        # Interface for similar colors
        similar_colors: List[SimilarColorConfig] = []
        while questionary.confirm("Add a group of similar colors?").ask():
            main = cast(
                str, questionary.select("Main color:", choices=[f"{c.name} ({c.value})" for c in ColorID]).ask()
            )
            similar = cast(
                List[str],
                questionary.checkbox("Similar colors:", choices=[f"{c.name} ({c.value})" for c in ColorID]).ask(),
            )
            main_id = int(main.split("(")[1][:-1])
            similar_ids = {int(c.split("(")[1][:-1]) for c in similar}
            similar_colors.append({"main_color": main_id, "similar_colors": list(similar_ids)})
        # Save the configuration
        config.color_priorities = cast(List[Dict[str, int]], priorities)
        config.ignored_source_colors = ignored_source_colors
        config.ignored_board_colors = ignored_board_colors
        config.similar_colors = cast(List[Dict[str, int]], similar_colors)
        config.save()
        return priorities, ignored_source_colors, ignored_board_colors, similar_colors
