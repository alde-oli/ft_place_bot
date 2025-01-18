# FTPlace Image Maintainer

[![Release](https://img.shields.io/github/v/release/alde-oli/ft_place_bot?include_prereleases&style=flat-square)](https://github.com/alde-oli/ft_place_bot/releases)
[![CI Status](https://img.shields.io/github/actions/workflow/status/alde-oli/ft_place_bot/ci.yml?branch=main&style=flat-square)](https://github.com/alde-oli/ft_place_bot/actions)
[![License](https://img.shields.io/github/license/alde-oli/ft_place_bot?style=flat-square)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue?style=flat-square)](pyproject.toml)
[![Code Coverage](https://img.shields.io/codecov/c/github/alde-oli/ft_place_bot?style=flat-square)](https://codecov.io/gh/alde-oli/ft_place_bot)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=flat-square)](https://github.com/astral-sh/ruff)

## Download

You can download the latest version of FT Place Bot from the [Releases](https://github.com/alde-oli/ft_place_bot/releases) page.

FTPlace Image Maintainer is a Python application designed to maintain images on the FTPlace board. It uses the FTPlace API to interact with the board, retrieves its current state, and ensures that the target image is properly maintained on the board.

## Features

- Interactive configuration interface
- Automatic saving of previous settings
- Intuitive configuration of color priorities
- Automatic conversion of images to FTPlace colors
- Board monitoring and identification of pixels to correct
- Pixel placement according to priority rules
- Automatic token expiration management

## Prerequisites

- Python 3.9+

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/alde-oli/ft_place_bot.git
    cd ft_place_bot
    ```

2. Install poetry if not already installed:
    ```sh
    pip install poetry
    ```

3. Install dependencies:
    ```sh
    poetry install
    ```

## Usage

1. Run the application:
    ```sh
    poetry run ft_place_bot
    ```

2. Follow the interactive steps:
   - Configure access tokens (saved for future use)
   - Select the image to maintain
   - Define the coordinates on the board
   - Configure color priorities (optional, previous configuration reusable)

## Color Configuration

The interface allows you to easily configure:

- Priority levels for each color (1-3)
- Colors to ignore
- Groups of similar colors

Your configuration is automatically saved and can be reused in future runs.

## Configuration Files

Configurations are stored in:
- `~/.ft_place_bot_config.json`: Stores tokens, last position, and color configuration

## Components

### Interactive Interface (`interface.py`)
- User interaction management
- Configuration saving and loading

### API Client (`client_api.py`)
- Communication with the FTPlace API
- Token and request management

### Image Manager (`utils.py`)
- Image loading and conversion
- Color distance calculation

### Image Monitor (`image_monitor.py`)
- Board monitoring
- Intelligent pixel placement

## Contribution

Contributions are welcome! Feel free to open an issue or submit a pull request for any improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
