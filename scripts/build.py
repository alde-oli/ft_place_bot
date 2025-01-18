import argparse
import logging
import sys
from pathlib import Path
from subprocess import CalledProcessError, run  # nosec B404
from typing import List


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_IMPORTS = {
    "ft_place_bot.client.client_api",
    "ft_place_bot.config",
    "ft_place_bot.core.color_config",
    "ft_place_bot.core.image_monitor",
    "ft_place_bot.utils.utils",
}

# Whitelist of allowed PyInstaller options
ALLOWED_OPTIONS = {
    "--name=",
    "--onefile",
    "--clean",
    "--paths=",
    "--add-data=",
    "--hidden-import=",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Build script for ft_place_bot")
    parser.add_argument("--name", type=str, default="ft_place_bot", help="Name of the output executable")
    return parser.parse_args()


def validate_command(cmd: List[str]) -> bool:
    """Validate that the command only contains allowed options."""
    if not cmd or cmd[0] != sys.executable:
        return False

    if cmd[1:3] != ["-m", "PyInstaller"]:
        return False

    # Check all options are in whitelist
    for arg in cmd[3:]:
        if not any(arg.startswith(opt) for opt in ALLOWED_OPTIONS):
            if not arg.endswith(".py"):  # Allow .py files at the end
                return False

    return True


def validate_paths() -> tuple[Path, Path, Path]:
    """Validate all required paths exist."""
    base_dir = Path(__file__).parent.parent.resolve()
    main_path = base_dir / "ft_place_bot" / "__main__.py"
    readme_path = base_dir / "README.md"

    if not main_path.is_file():
        raise FileNotFoundError(f"Main script not found at: {main_path}")
    if not readme_path.is_file():
        raise FileNotFoundError(f"README not found at: {readme_path}")

    return base_dir, main_path, readme_path


def get_build_command(base_dir: Path, main_path: Path, readme_path: Path, name: str) -> List[str]:
    """Get the PyInstaller command with safe, validated arguments."""
    cmd = [
        sys.executable,  # Use the current Python interpreter
        "-m",
        "PyInstaller",
        f"--name={name}",  # Utilise le nom passé en argument
        "--onefile",
        "--clean",
        f"--paths={base_dir / 'ft_place_bot'}",
        f"--add-data={readme_path}:.",
    ]

    # Add validated hidden imports
    for import_path in sorted(ALLOWED_IMPORTS):
        cmd.append(f"--hidden-import={import_path}")

    # Add the main script last
    cmd.append(str(main_path))

    return cmd


def build() -> None:
    """Build the executable for the current platform with security checks."""
    try:
        args = parse_args()
        base_dir, main_path, readme_path = validate_paths()
        cmd = get_build_command(base_dir, main_path, readme_path, args.name)

        if not validate_command(cmd):
            raise ValueError("Invalid build command detected")

        logger.info("Starting build process...")
        logger.info("Building executable with name: %s", {args.name})

        # We explicitly validate the command above, so this is safe
        result = run(  # nosec B603
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )

        if result.stdout:
            logger.info(result.stdout)

        logger.info("Build completed successfully")

    except FileNotFoundError as e:
        logger.error("File not found: %s", str(e))
        sys.exit(2)
    except CalledProcessError as e:
        logger.error("Build process failed: %s", str(e))
        if e.stderr:
            logger.error("Error output: %s", e.stderr)
        sys.exit(1)
    except ValueError as e:
        logger.error("Validation error: %s", str(e))
        sys.exit(1)


if __name__ == "__main__":
    build()
