# FTPlace Image Maintainer

FTPlace Image Maintainer is a Python project designed to monitor and maintain images on the FTPlace board. It uses an API to interact with the board, fetches the current state, and ensures that the target image is correctly represented on the board.

## Features

- Fetches user profile and board data from the FTPlace API.
- Converts target images to the closest FTPlace colors.
- Monitors the board and identifies pixels that need to be fixed.
- Places pixels on the board according to priority and color rules.
- Handles token expiration and retries failed requests.

## Requirements

- Python 3.7+
- `requests`
- `numpy`
- `Pillow`

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/ft_place_bot.git
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

    - [img_path](http://_vscodecontentref_/0): Path to the image to maintain.
    - [origin_x](http://_vscodecontentref_/1): X coordinate of the origin on the board.
    - [origin_y](http://_vscodecontentref_/2): Y coordinate of the origin on the board.
    - [access_token](http://_vscodecontentref_/3): Your access token for the FTPlace API.
    - [refresh_token](http://_vscodecontentref_/4): Your refresh token for the FTPlace API.

## Example

```sh
python -m ft_place_bot example_image.png 10 20 your_access_token your_refresh_token
```

## Configuration

The color configuration and API settings can be adjusted in the 

config.py

 and 

color_config.py

 files. You can define color priorities, ignored colors, and sets of similar colors.

## Logging

The script logs its activities, including connection status, image conversion, and pixel placement, to the console. You can adjust the logging settings in the 

setup_logging

 function in 

__main__.py

.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
