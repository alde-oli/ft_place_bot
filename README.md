<!-- YoRHa archive -->
```
▸ YoRHa // ARCHIVE — FT_PLACE_BOT
```

An interactive Python bot that keeps a pixel-art image intact on FTPlace, 42 Lausanne's shared r/place-style board, by watching the board and repainting wrong pixels in priority order.

[![Release](https://img.shields.io/github/v/release/alde-oli/ft_place_bot?include_prereleases&style=flat-square&color=4e4b42)](https://github.com/alde-oli/ft_place_bot/releases)
[![Python](https://img.shields.io/badge/python-3.9%2B-4e4b42?style=flat-square)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-dad4bb?style=flat-square)](LICENSE)

| UNIT DATA | |
|---|---|
| Type | Personal project (built for a 42 Lausanne community event) |
| Stack | Python 3.9+ · requests · NumPy · Pillow · pydantic · questionary · Poetry · PyInstaller |
| Status | □ ARCHIVED · last release `v0.8.0` |

## ▸ Overview
FTPlace gives each user a limited pixel budget on a shared board, and other users keep drawing over you.
This bot loads a target image, maps every pixel to the nearest board colour (Euclidean RGB distance), then loops:
fetch the board, compute how much of the image is correct, pick the highest-priority wrong pixel and place it,
sleeping exactly until the next pixel timer when the API answers "too early" (HTTP 425).
Expired sessions (HTTP 426) are handled by reading the refreshed tokens from `Set-Cookie` and replaying the request.

## ▸ Features
- Interactive terminal setup (questionary): tokens, image path, board origin, colour rules
- Every choice saved to `~/.ft_place_bot_config.json` and offered again on the next run
- Automatic conversion of any image to the board palette
- Colour rules: priority levels 1–3, colours to ignore in the source image or on the board, groups of "similar" colours treated as equal
- Live progress log: correct / total pixels and completion percentage
- Retry with backoff on 5xx errors, token refresh on expiry, wait-until-timer on rate limit
- Cross-platform single-file binaries (Linux, Windows, macOS) built by a GitHub Actions release workflow

## ▸ Usage
Download a binary from the [Releases](https://github.com/alde-oli/ft_place_bot/releases) page, or run from source:

```bash
git clone https://github.com/alde-oli/ft_place_bot.git
cd ft_place_bot
pip install poetry
poetry install
poetry run ft_place_bot
```

Then follow the prompts: access / refresh tokens (taken from your FTPlace session cookies), image to maintain, X/Y position on the board, and optionally the colour rules.

Build a standalone executable locally (PyInstaller, output in `dist/`):

```bash
poetry install --with dev
poetry run python scripts/build.py --name ft_place_bot
```

Helper: `python scripts/png_to_cores_json.py <image.png>` converts an image to a JSON pixel pattern (`{x, y, color}` list) using the board palette.

## ▸ Structure
```
ft_place_bot/
├── __main__.py           entry point: setup, then the maintenance loop
├── interface.py          interactive prompts + saved configuration
├── config.py             palette IDs, API endpoints, status codes, user config model
├── client/client_api.py  HTTP session, retries, token refresh
├── core/image_monitor.py board diff, pixel prioritisation, placement loop
├── core/color_config.py  priority / ignore / similar-colour rules
└── utils/utils.py        image loading and palette conversion
scripts/                  PyInstaller build script, PNG → JSON converter
pictures/                 sample pixel-art targets
```

## ▸ Notes
- Tooling: CI runs safety, bandit and mypy (strict); pre-commit runs ruff and bandit. There is no test suite yet (the test step is commented out in CI).
- The API base URL is hardcoded in `__main__.py` for the FTPlace instance the bot was written for.

---
<sub>▸ Archived by UNIT ALDE-OLI · [profile](https://github.com/alde-oli)</sub>
