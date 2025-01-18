# FTPlace Image Maintainer

FTPlace Image Maintainer is a Python project designed to monitor and maintain images on the FTPlace board. It uses an API to interact with the board, fetches the current state, and ensures that the target image is correctly represented on the board.

## Features

- Fetches user profile and board data from the FTPlace API.
- Converts target images to the closest FTPlace colors.
- Monitors the board and identifies pixels that need to be fixed.
- Places pixels on the board according to priority and color rules.
- Handles token expiration and retries failed requests.

## Requirements

- Python 3.9+
- `requests`
- `numpy`
- `Pillow`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/alde-oli/ft_place_bot.git
    cd ft_place_bot
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Prepare your image and note its path.
2. Obtain your access and refresh tokens from the FTPlace API.
3. Run the script with the required arguments:
    ```sh
    python -m ft_place_bot <img_path> <origin_x> <origin_y> <access_token> <refresh_token>
    ```

    - `img_path`: Path to the image to maintain.
    - `origin_x`: X coordinate of the origin on the board.
    - `origin_y`: Y coordinate of the origin on the board.
    - `access_token`: Your access token for the FTPlace API.
    - `refresh_token`: Your refresh token for the FTPlace API.

## Example

```sh
python -m ft_place_bot example_image.png 10 20 your_access_token your_refresh_token
```

## Configuration

The color configuration and API settings can be adjusted in the `config.py` and `color_config.py` files. You can define color priorities, ignored colors, and sets of similar colors.

### API Configuration

The `APIConfig` class in `config.py` allows you to configure the API settings:

- `base_url`: The base URL of the FTPlace API.
- `refresh_token`: The refresh token for authentication.
- `access_token`: The access token for authentication.
- `retry_attempts`: Number of retry attempts for failed requests.
- `check_interval`: Interval in seconds between checks.

### Color Configuration

The `ColorConfig` class in `color_config.py` allows you to configure color priorities and ignored colors:

- `priorities`: A list of `ColorPriority` objects defining the priority levels for different colors.
- `ignored_source_colors`: A set of color IDs to ignore in the source image.
- `ignored_board_colors`: A set of color IDs to ignore on the board.
- `color_sets`: A list of `ColorSet` objects defining sets of similar colors.

### Example Color Configuration

```python
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
```

## Logging

The script logs its activities, including connection status, image conversion, and pixel placement, to the console. You can adjust the logging settings in the `setup_logging` function in `__main__.py`.

## Components

### `client_api.py`

Defines the `FTPlaceAPI` class which handles communication with the FTPlace API, including setting up the session, handling responses, and fetching user profile and board data.

### `color_config.py`

Defines the `ColorConfig`, `ColorPriority`, and `ColorSet` classes which manage the color configuration, including priorities and ignored colors.

### `config.py`

Defines the `APIConfig` class and various enums for API endpoints and HTTP statuses.

### `exceptions.py`

Defines custom exceptions for handling errors related to the FTPlace API.

### `image_monitor.py`

Defines the `ImageMonitor` class which monitors the board, calculates image statistics, identifies pixels to fix, and handles pixel placement.

### `models.py`

Defines data models such as `Pixel` and `UserProfile` for representing pixel data and user profiles.

### `utils.py`

Defines utility functions and classes such as `ColorManager` for loading images, converting colors, and calculating color distances.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
