#!/usr/bin/env python3

"""This module updates a given alacritty.toml file with a given colorscheme TOML file."""

from os.path import expanduser
from shutil import copyfile
from tempfile import NamedTemporaryFile
from enum import Enum, auto
import tomlkit


class OverwriteBehaviour(Enum):
    """Decides what should happen to previously existing entries in the colors
    part of your config."""

    UPDATE_INTERLEAVE = auto()
    REPLACE = auto()


def update_colors_in_config_dict(
    config: tomlkit.TOMLDocument,
    colors: tomlkit.TOMLDocument,
    behaviour: OverwriteBehaviour = OverwriteBehaviour.REPLACE,
) -> None:
    """Update the TOML dictionary `config` with the data from `colors`."""
    match behaviour:
        case OverwriteBehaviour.REPLACE:
            config["colors"] = colors["colors"]
        case OverwriteBehaviour.UPDATE_INTERLEAVE:
            config["colors"].update(colors["colors"])


def load_toml_config_from(path: str) -> tomlkit.TOMLDocument:
    """Open the TOML file at full path `path` and load TOML from it."""
    try:
        with open(path, "r", encoding="utf-8") as config_file:
            return tomlkit.load(config_file)
    except OSError as exc:
        msg = f"Could not open Alacritty configuration file at {path=}."
        raise RuntimeError(msg) from exc


def replace_colorscheme_at(
    config_path: str,
    colors_path: str,
    behaviour: OverwriteBehaviour = OverwriteBehaviour.REPLACE,
) -> None:
    """Update the configuration at `config_path` with the TOML colors file at `colors_path`."""
    config_path = expanduser(config_path)
    colors_path = expanduser(colors_path)

    config = load_toml_config_from(config_path)
    colors = load_toml_config_from(colors_path)

    update_colors_in_config_dict(config, colors, behaviour=behaviour)

    # Write to a temporary file and replace the config.
    with NamedTemporaryFile(encoding='utf-8', mode='w+') as tmp_file:
        tomlkit.dump(config, tmp_file)
        # TODO(akiss-xyz, 2024-01-03): Is this flush really required?
        # Didn't seem to work for me without it...
        tmp_file.flush()
        copyfile(tmp_file.name, config_path)
