#!/usr/bin/env python3

"""Test cases for the TOML version of alacritty_colorscheme."""

import os
from os import path
from shutil import copyfile, rmtree, copytree
from pytest import raises, fixture
import tomlkit
from alacritty_colorscheme.colorscheme_toml import (
    load_toml_config_from,
    replace_colorscheme_at,
    update_colors_in_config_dict,
    OverwriteBehaviour,
)

# The top of the test directory
ROOT = os.getcwd() + "/tests/test-config-toml/"


@fixture
def test_toml_config_path(tmpdir):
    """Creates a temporary copy of ./test-config-toml for testing."""

    tmpdir_path = str(tmpdir)
    original_path = "./tests/test-config-toml"
    test_path = path.join(tmpdir_path, "test-config-toml")
    if path.exists(test_path):
        rmtree(test_path)
    copytree(original_path, test_path)

    return test_path


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


def test_apply_colorscheme_to_toml_config_with_default_arg(test_toml_config_path):
    """Checks that the user can just specify a colorscheme without a config
    file, and the correct config file will automatically be chosen."""

    # Import the CLI module locally so we can poke around with it.
    import alacritty_colorscheme.cli as cli

    # Override defaults temporarily for test
    cli.DEFAULT_CONFIG_PATH_OPTIONS = [
        # Does not exist, should be skipped
        path.join(test_toml_config_path, "alacritty.yml"),
        # Real config
        path.join(test_toml_config_path, "alacritty.toml")
    ]
    cli.DEFAULT_COLORSCHEME_DIR = path.join(test_toml_config_path, "colors")
    cli.ArgumentParser.colorscheme_dir = cli.DEFAULT_COLORSCHEME_DIR

    parser = cli.create_parser()
    args = parser.parse_args(["apply", "hyper.toml"])

    # Execute the command
    cli.handle_args(args)

    # Check that the correct changes were made
    conf = load_toml_config_from(path.join(test_toml_config_path, "alacritty.toml"))

    assert conf['colors']['primary']['background'] == '#000000'


def test_apply_with_no_config_file_to_be_found(test_toml_config_path):
    """Check behaviour when no config files exist."""

    # Import the CLI module locally so we can poke around with it.
    import alacritty_colorscheme.cli as cli

    # Override defaults temporarily for test
    cli.DEFAULT_CONFIG_PATH_OPTIONS = [
        path.join(test_toml_config_path, "does_not_exist.toml"),
        path.join(test_toml_config_path, "fake.toml"),
        path.join(test_toml_config_path, "not_real.toml")
    ]
    cli.DEFAULT_COLORSCHEME_DIR = path.join(test_toml_config_path, "colors")
    cli.ArgumentParser.colorscheme_dir = cli.DEFAULT_COLORSCHEME_DIR

    parser = cli.create_parser()
    with raises(RuntimeError):
        args = parser.parse_args(["apply", "hyper.toml"])
