#!/usr/bin/env python3

import os

from enum import Enum, auto
from tap import Tap
from os.path import expanduser, isfile, join
from typing import List, Optional, cast

try:
    from typing import Literal  # type: ignore
except ImportError:
    from typing_extensions import Literal

from . import __version__
from .colorscheme_yaml import (
    get_applied_colorscheme,
    get_applicable_colorscheme,
    replace_colorscheme,
)
from .colorscheme_toml import TomlManager


# The list of recognized file endings for configuration and color files.
CONF_FILE_ENDINGS = (".toml", ".yml", ".yaml")
# The default configuration file path, in priority order.
DEFAULT_CONFIG_PATH_OPTIONS: List[str] = [
    expanduser(join("~", ".config/alacritty/alacritty.toml")),
    expanduser(join("~", ".config/alacritty/alacritty.yml")),
]
# The default directory to search colorschemes for.
DEFAULT_COLORSCHEME_DIR = join("~", ".config/alacritty/colors/")


class ConfigType(Enum):
    YAML_CONFIG = auto()
    TOML_CONFIG = auto()


def get_config_type(config_file: str) -> ConfigType:
    if config_file.endswith(("yaml", "yml")):
        return ConfigType.YAML_CONFIG
    elif config_file.endswith("toml"):
        return ConfigType.TOML_CONFIG
    else:
        raise RuntimeError(
            f"Unknown config type, please check file ending of {config_file=}"
        )


class StatusParser(Tap):
    pass


# TODO: filter dark and light backgrounds
class ListParser(Tap):
    pass


class ApplyParser(Tap):
    colorscheme: str

    def configure(self) -> None:
        self.add_argument("colorscheme")


class ToggleParser(Tap):
    colorschemes: List[str] = []
    reverse: bool = False

    def configure(self) -> None:
        self.add_argument("colorschemes")


class ArgumentParser(Tap):
    # config_file: str = config_path  # Path to alacritty configuration file
    config_file: str
    colorscheme_dir: str = DEFAULT_COLORSCHEME_DIR  # Path to colorscheme directory
    base16_vim: bool = (
        False  # Support base16-vim. Generates .vimrc_background file at home directory
    )
    debug: bool = False  # Show more information
    # version: str  # Version

    def configure(self) -> None:
        self.add_subparsers(help="sub-command help", dest="_subparser_name")
        self.add_subparser("list", ListParser, help="List available colorschemes")
        self.add_subparser("status", StatusParser, help="Show current colorscheme")
        self.add_subparser("toggle", ToggleParser, help="Toggle colorscheme")
        self.add_subparser("apply", ApplyParser, help="Apply colorscheme")

        self.add_argument(
            "-c", "--config_file", metavar="configuration file", default=None
        )

        self.add_argument("-C", "--colorscheme_dir", metavar="colorscheme directory")

        self.add_argument("-V", "--base16_vim")

        self.add_argument("-d", "--debug")

        self.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s {version}".format(version=__version__),
        )

    def _get_config_file(self) -> str:
        """Get the path to the config file to be used."""
        if self.config_file is None:
            # Default to the best option in DEFAULT_CONFIG_PATH_OPTIONS.
            options = list(filter(os.path.exists, DEFAULT_CONFIG_PATH_OPTIONS))
            if len(options) == 0:
                msg = (
                    "No config file could be found! We tried the following:\n"
                    + f"{DEFAULT_CONFIG_PATH_OPTIONS}\n"
                    + "Place your configuration file at one of those locations, "
                    + "or specify a different one with --config_file <file>."
                )
                raise RuntimeError(msg)

            return options[0]

        return self.config_file

    def process_args(self):
        self.config_file = self._get_config_file()


# NOTE: adding '_subparser_name' to ArgumentParser will add a new argument.
# So, creating this class for type casting purpose only
class TypedArgumentParser(ArgumentParser):
    _subparser_name: Literal["list", "status", "toggle", "apply"]


def create_parser() -> TypedArgumentParser:
    parser = ArgumentParser(
        "alacritty-colorscheme",
        description="Change colorscheme of alacritty with ease.",
    )
    return cast(TypedArgumentParser, parser)


def get_files_in_directory(path: str) -> Optional[List[str]]:
    expanded_path = expanduser(path)
    if not os.path.isdir(expanded_path):
        raise RuntimeError(
            f"Directory {expanded_path=} does not exist or is not a directory."
        )
    try:
        onlyfiles = []
        for root, _dirs, files in os.walk(expanded_path, followlinks=True):
            for file in files:
                full_path = join(root, file)
                if file.endswith(CONF_FILE_ENDINGS) and isfile(full_path):
                    onlyfiles.append(full_path.removeprefix(expanded_path))
        onlyfiles.sort()
        return onlyfiles
    except OSError:
        return None


def handle_args(args: TypedArgumentParser) -> None:
    if args._subparser_name == "list":
        files = get_files_in_directory(args.colorscheme_dir)
        if files is None:
            raise RuntimeError(f"Could not find directory: {args.colorscheme_dir}")
        for file in files:
            print(file)
    elif args._subparser_name == "status":
        try:
            colorscheme = get_applied_colorscheme(args.config_file)
            if colorscheme is None:
                print("No colorscheme is applied")
            else:
                print(colorscheme)
        except OSError:
            raise RuntimeError(
                f"Could not find a valid alacritty config file: {args.config_file}"
            )
    elif args._subparser_name == "toggle":
        try:
            colorscheme = get_applied_colorscheme(args.config_file)
        except OSError:
            raise RuntimeError(
                f"Could not find a valid alacritty config file: {args.config_file}"
            )

        toggleArgs = cast(ToggleParser, args)
        colorschemes = (
            toggleArgs.colorschemes
            if toggleArgs.colorschemes
            else get_files_in_directory(args.colorscheme_dir)
        )

        if colorschemes is None:
            raise RuntimeError(f"Could not find directory {args.colorscheme_dir}")

        applicable_colorscheme = get_applicable_colorscheme(
            colorschemes,
            colorscheme,
            toggleArgs.reverse,
        )
        if applicable_colorscheme is None:
            raise RuntimeError("Could not find an applicable colorscheme")

        colors_path = join(args.colorscheme_dir, applicable_colorscheme.lstrip("/"))
        replace_colorscheme(
            colors_path,
            args.config_file,
            applicable_colorscheme,
            args.base16_vim,
            args.debug,
        )
    elif args._subparser_name == "apply":
        applyArgs = cast(ApplyParser, args)
        colors_path = expanduser(
            join(args.colorscheme_dir, applyArgs.colorscheme.lstrip("/"))
        )

        if not colors_path.endswith(CONF_FILE_ENDINGS):
            # Assume we were just given a color scheme name, no file extension.
            # Try to find one that exists.
            options = list(
                filter(os.path.exists, [colors_path + end for end in CONF_FILE_ENDINGS])
            )
            if len(options) == 0:
                raise RuntimeError(
                    f"Cannot find theme {applyArgs.colorscheme.lstrip('/')}"
                    + f" under '{args.colorscheme_dir}'."
                )
            colors_path = list(options)[0]

        # Apply the color scheme appropriate to the configuration file type.
        match get_config_type(args.config_file):
            case ConfigType.TOML_CONFIG:
                # New TOML configs.

                if colors_path.endswith(("yml", "yaml")):
                    raise RuntimeError(
                        f"Attempted to apply a YAML color scheme '{colors_path}'"
                        + f" to a TOML configuration file '{args.config_file}'."
                    )

                TomlManager.replace_colorscheme_at(args.config_file, colors_path)

            case ConfigType.YAML_CONFIG:
                # Old YAML configs.

                if colors_path.endswith("toml"):
                    raise RuntimeError(
                        f"Attempted to apply a TOML color scheme '{colors_path}'"
                        + f" to a YAML configuration file '{args.config_file}'."
                    )

                replace_colorscheme(
                    colors_path,
                    args.config_file,
                    applyArgs.colorscheme,
                    args.base16_vim,
                    args.debug,
                )
    else:
        args.print_usage()


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    try:
        handle_args(args)
    except RuntimeError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
