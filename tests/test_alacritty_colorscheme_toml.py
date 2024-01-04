#!/usr/bin/env python3

"""Test cases for the TOML version of alacritty_colorscheme."""

import os
from shutil import copyfile
import tomlkit
from alacritty_colorscheme.colorscheme_toml import (
    load_toml_config_from,
    replace_colorscheme_at,
    update_colors_in_config_dict,
    OverwriteBehaviour,
)

# The top of the test directory
ROOT = os.getcwd() + "/tests/test-config-toml/"


def test_loading_toml_files():
    """Check basic opening/loading of TOML files."""

    conf = load_toml_config_from(ROOT + "/alacritty.1.toml")

    assert isinstance(conf, tomlkit.TOMLDocument)
    assert conf["window"]["padding"]["x"] == 0
    assert conf["window"]["dimensions"]["columns"] == 293


def test_basic_color_updates():
    """Checks updating of TOML files."""
    original_path = ROOT + "/alacritty.1.toml"
    test_conf_path = ROOT + "/tmp/alacritty.1.toml"
    copyfile(original_path, test_conf_path)

    replace_colorscheme_at(test_conf_path, ROOT + "/colors/cob.toml")

    # Now diff the two

    original = load_toml_config_from(original_path)
    test_conf = load_toml_config_from(test_conf_path)

    assert original["colors"]["bright"]["black"] == "0xdeadbe"
    assert test_conf["colors"]["bright"]["black"] == "0x10151b"


def test_overwrite_behaviour_replace():
    """Makes sure OverwriteBehaviour.REPLACE gets rid of prior entries under 'colors'."""

    conf = tomlkit.parse(
        """
    live_config_reload = true

    [bell]
    duration = 0

    [colors]
    weird_entry_to_remove = true
    [colors.bright]
    black = "0xffffff"
    """
    )

    colors = tomlkit.parse(
        """
    [colors]
    [colors.bright]
    black = "0x000000"
    """
    )

    assert conf["colors"]["bright"]["black"] != colors["colors"]["bright"]["black"]
    assert "weird_entry_to_remove" in conf["colors"]

    update_colors_in_config_dict(conf, colors)

    assert conf["colors"]["bright"]["black"] == colors["colors"]["bright"]["black"]
    assert "weird_entry_to_remove" not in conf["colors"]


def test_overwrite_behaviour_update_interleave():
    """Makes sure OverwriteBehaviour.UPDATE_INTERLEAVE maintains any prior entries
    under 'colors'."""

    conf = tomlkit.parse(
        """
    live_config_reload = true

    [bell]
    duration = 0

    [colors]
    weird_entry_to_remove = true
    [colors.bright]
    black = "0xffffff"
    """
    )

    colors = tomlkit.parse(
        """
    [colors]
    [colors.bright]
    black = "0x000000"
    """
    )

    assert conf["colors"]["bright"]["black"] != colors["colors"]["bright"]["black"]
    assert "weird_entry_to_remove" in conf["colors"]

    update_colors_in_config_dict(
        conf, colors, behaviour=OverwriteBehaviour.UPDATE_INTERLEAVE
    )

    assert conf["colors"]["bright"]["black"] == colors["colors"]["bright"]["black"]
    assert "weird_entry_to_remove" in conf["colors"]
