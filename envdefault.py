"""
envdefault.py

A simple utility class for use with argparse that allows command-line arguments
to fall back to environment variables or values in a .env file.
"""

from collections import ChainMap
import os

# Supports python-dotenv; check if installed:
try:
    from dotenv import dotenv_values

    _use_dotenv = True
except ImportError:
    _use_dotenv = False


class EnvDefault:
    """
    A helper class to resolve default values for CLI arguments from environment
    variables or a .env file.

    Priority order:
        1. Environment variable (os.environ)
        2. .env file (manually parsed if python-dotenv is not installed)

    Example:
        parser.add_argument(
            "--token",
            default=EnvDefault("API_TOKEN")(),
            required=EnvDefault("API_TOKEN")() is None
        )
    """

    _dotenv_loaded: bool = False
    _dotenv_values: dict[str, str] = {}

    def __init__(self, name: str, /, *, env_file: str = ".env") -> None:
        """
        Args:
            name (str): The name of the environment variable to look up.
            env_file (str): The path to the .env file (default is ".env").
        """
        self.name = name
        self.env_file = env_file
        self._load_dotenv()

    def _load_dotenv(self) -> None:
        """
        Loads values from the .env file into a shared class-level dictionary.
        This is only run once per process.
        """
        if EnvDefault._dotenv_loaded:
            return

        if _use_dotenv:
            EnvDefault._dotenv_values = dotenv_values(self.env_file)
        else:
            try:
                with open(self.env_file) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, val = line.split("=", 1)
                        EnvDefault._dotenv_values[key.strip()] = val.strip()
            except FileNotFoundError:
                pass

        EnvDefault._dotenv_loaded = True

    def __call__(self) -> str | None:
        """
        Returns the value for the environment variable from:
        os.environ -> .env -> None.

        Returns:
            str | None: The resolved value or None if not found.
        """
        # Use ChainMap:
        return ChainMap(os.environ, EnvDefault._dotenv_values).get(self.name)

        # Alternatively:
        # return os.environ.get(
        #    self.name, EnvDefault._dotenv_values.get(self.name)
        # )


if __name__ == "__main__":
    # Sample usage
    import argparse

    parser = argparse.ArgumentParser()

    username_default = EnvDefault("USERNAME")()
    password_default = EnvDefault("PASSWORD")()

    parser.add_argument(
        "--username",
        default=username_default,
        required=username_default is None,
        help="Username (from CLI > ENV > .env)",
    )

    parser.add_argument(
        "--password",
        default=password_default,
        required=password_default is None,
        help="Password (from CLI > ENV > .env)",
    )

    args = parser.parse_args()
    print("Username:", args.username)
    print("Password:", args.password)
