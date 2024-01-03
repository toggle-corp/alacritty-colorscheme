#!/usr/bin/env python3

"""This module converts YAML color schemes to TOML equivalents."""

from typing import Optional
from os.path import expanduser
import tomlkit
from ruamel.yaml import YAML

# YAML parser/writer
yaml = YAML()


def load_yaml_colorscheme_from(yaml_path: str) -> YAML:
    """Load the YAML colorscheme from the file at `yaml_path`."""
    try:
        with open(yaml_path, "r", encoding="utf-8") as colorscheme_file:
            return yaml.load(colorscheme_file)
    except OSError as exc:
        msg = f"Could not open YAML colorscheme file at {yaml_path=}."
        raise RuntimeError(msg) from exc


def create_equivalent_toml_to_yaml(original: YAML) -> tomlkit.TOMLDocument:
    """Creates a TOML document with the same contents as the YAML input.
    Copies only the 'colors' table over."""
    toml_equivalent = tomlkit.document()

    colors = tomlkit.table()
    colors.update(original["colors"])

    toml_equivalent.add("colors", colors)

    return toml_equivalent


def convert_yaml_colorscheme_to_toml_at(
    yaml_path: str, toml_out_path: Optional[str] = None
) -> None:
    """Reads the YAML colorscheme at `yaml_path` and outputs a TOML equivalent."""
    assert yaml_path.endswith((".yml", ".yaml"))

    yaml_path = expanduser(yaml_path)
    if toml_out_path is None:
        toml_out_path = yaml_path.replace(".yml", ".toml").replace(".yaml", ".toml")

    original_yaml = load_yaml_colorscheme_from(yaml_path)
    toml_equivalent = create_equivalent_toml_to_yaml(original_yaml)

    with open(toml_out_path, "w+", encoding="utf=8") as toml_file:
        tomlkit.dump(toml_equivalent, toml_file)
