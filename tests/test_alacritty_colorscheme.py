from alacritty_colorscheme import __version__
from alacritty_colorscheme.cli import handle_args, create_parser
from alacritty_colorscheme.yml_to_toml import load_yaml_file_from
from shutil import copytree, rmtree
from pytest import raises, fixture
from os import path


@fixture
def test_config_path(tmpdir):
    tmpdir_path = str(tmpdir)
    original_path = './tests/test-config'
    test_path = path.join(tmpdir_path, 'test-config')
    if (path.exists(test_path)):
        rmtree(test_path)
    copytree(original_path, test_path)

    return test_path


def test_version():
    assert __version__ == '1.0.2'


def test_noarg():
    parser = create_parser()
    args = parser.parse_args([])
    assert args._subparser_name is None


def test_list_existing(tmpdir):
    tmpdir_path = str(tmpdir)
    parser = create_parser()
    args = parser.parse_args(['--colorscheme_dir', tmpdir_path, 'list'])
    handle_args(args)


def test_list_no_colorscheme():
    with raises(RuntimeError):
        parser = create_parser()
        args = parser.parse_args(['--colorscheme_dir', 'this-dir-does-not-exist', 'list'])
        handle_args(args)


def test_status_no_config():
    with raises(RuntimeError):
        parser = create_parser()
        args = parser.parse_args(['--config_file', 'this-config-does-not-exist', 'status'])
        handle_args(args)


def test_status_with_config():
    parser = create_parser()
    args = parser.parse_args(['--config_file', './tests/test-config/alacritty-with-color.yml', 'status'])
    handle_args(args)


def test_status_with_config_without_colors():
    parser = create_parser()
    args = parser.parse_args(['--config_file', './tests/test-config/alacritty-without-color.yml', 'status'])
    handle_args(args)


def test_apply_with_config(test_config_path):
    parser = create_parser()
    args = parser.parse_args([
        '--config_file', path.join(test_config_path, 'alacritty-with-color.yml'),
        '--colorscheme_dir', path.join(test_config_path, 'colors'),
        'apply', 'base16-zenburn.yml',
    ])
    handle_args(args)


def test_apply_with_bad_color_option(test_config_path):
    with raises(RuntimeError):
        parser = create_parser()
        args = parser.parse_args([
            '--config_file', path.join(test_config_path, 'alacritty-with-color.yml'),
            '--colorscheme_dir', path.join(test_config_path, 'colors'),
            'apply', 'base16-zenbum.yml',
        ])
        handle_args(args)


def test_apply_with_config_without_color(test_config_path):
    parser = create_parser()
    args = parser.parse_args([
        '--config_file', path.join(test_config_path, 'alacritty-with-color.yml'),
        '--colorscheme_dir', path.join(test_config_path, 'colors'),
        'apply', 'base16-zenburn.yml',
    ])
    handle_args(args)


def test_toggle(test_config_path):
    parser = create_parser()
    args = parser.parse_args([
        '--config_file', path.join(test_config_path, 'alacritty-with-color.yml'),
        '--colorscheme_dir', path.join(test_config_path, 'colors'),
        'toggle'
    ])
    handle_args(args)


def test_toggle_in_list(test_config_path):
    parser = create_parser()
    args = parser.parse_args([
        '--config_file', path.join(test_config_path, 'alacritty-without-color.yml'),
        '--colorscheme_dir', path.join(test_config_path, 'colors'),
        'toggle',
        'base16-spacemacs.yml',
        'base16-zenburn.yml',
    ])
    handle_args(args)


def test_apply_colorscheme_to_yml_config_with_default_arg(test_config_path):
    """Checks that the user can just specify a colorscheme without a config
    file, and the correct config file will automatically be chosen."""

    # Import the CLI module locally so we can poke around with it.
    import alacritty_colorscheme.cli as cli

    # Override defaults temporarily for test
    cli.DEFAULT_CONFIG_PATH_OPTIONS = [
        # TOML option which doesn't exist, should be skipped:
        path.join(test_config_path, "alacritty-without-color.toml"),
        # YAML option which should be taken as default:
        path.join(test_config_path, "alacritty-without-color.yml"),
    ]
    cli.DEFAULT_COLORSCHEME_DIR = path.join(test_config_path, "colors")
    cli.ArgumentParser.colorscheme_dir = cli.DEFAULT_COLORSCHEME_DIR

    parser = cli.create_parser()
    args = parser.parse_args(["apply", "base16-ocean.yml"])

    # Execute the command
    cli.handle_args(args)

    # Check that the correct changes were made
    conf = load_yaml_file_from(path.join(test_config_path, "alacritty-without-color.yml"))

    assert conf["colors"]["primary"]["background"] == "0x2b303b"
