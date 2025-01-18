from pathlib import Path
from typing import Tuple

import questionary
from config import ColorID, UserConfiguration


class Interface:
    @staticmethod
    def get_tokens() -> Tuple[str, str]:
        config = UserConfiguration.load()

        if config.access_token and config.refresh_token:
            use_saved = questionary.confirm("Use saved tokens?", default=True).ask()

            if use_saved:
                return config.access_token, config.refresh_token

        access_token = questionary.text("Access Token:").ask()
        refresh_token = questionary.text("Refresh Token:").ask()

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

        image_path = questionary.path("Image path:", validate=lambda x: Path(x).exists()).ask()

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

        origin_x = questionary.text("Position X:", validate=lambda x: x.isdigit()).ask()
        origin_y = questionary.text("Position Y:", validate=lambda x: x.isdigit()).ask()

        config.last_origin_x = int(origin_x)
        config.last_origin_y = int(origin_y)
        config.save()

        return int(origin_x), int(origin_y)

    @staticmethod
    def configure_colors() -> Tuple[list, set, list]:
        config = UserConfiguration.load()

        if config.color_priorities:
            use_saved = questionary.confirm("Use saved color configuration?", default=True).ask()

            if use_saved:
                return (config.color_priorities, config.ignored_colors, config.similar_colors)

        # Interface to configure priorities
        priorities = []
        while questionary.confirm("Add a priority?").ask():
            level = questionary.text("Priority level (1-3):", validate=lambda x: x in ["1", "2", "3"]).ask()

            colors = questionary.checkbox("Select colors:", choices=[f"{c.name} ({c.value})" for c in ColorID]).ask()

            color_ids = {int(c.split("(")[1][:-1]) for c in colors}
            priorities.append({"priority_level": int(level), "color_ids": list(color_ids)})

        # Interface for ignored colors
        ignored = questionary.checkbox(
            "Select colors to ignore:", choices=[f"{c.name} ({c.value})" for c in ColorID]
        ).ask()
        ignored_colors = {int(c.split("(")[1][:-1]) for c in ignored}

        # Interface for similar colors
        similar_colors = []
        while questionary.confirm("Add a group of similar colors?").ask():
            main = questionary.select("Main color:", choices=[f"{c.name} ({c.value})" for c in ColorID]).ask()

            similar = questionary.checkbox("Similar colors:", choices=[f"{c.name} ({c.value})" for c in ColorID]).ask()

            main_id = int(main.split("(")[1][:-1])
            similar_ids = {int(c.split("(")[1][:-1]) for c in similar}
            similar_colors.append({"main_color": main_id, "similar_colors": list(similar_ids)})

        # Save the configuration
        config.color_priorities = priorities
        config.ignored_colors = ignored_colors
        config.similar_colors = similar_colors
        config.save()

        return priorities, ignored_colors, similar_colors
