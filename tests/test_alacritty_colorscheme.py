from alacritty_colorscheme import __version__
from alacritty_colorscheme.cli import main, create_parser
from pytest import raises


def test_version():
    assert __version__ == '1.0.0'


def test_noarg():
    parser = create_parser()
    args = parser.parse_args([])
    assert args._subparser_name is None


def test_list_existing(tmpdir):
    parser = create_parser()
    args = parser.parse_args(['--colorscheme_dir', str(tmpdir), 'list'])
    main(args)


def test_list_non_existing():
    with raises(RuntimeError):
        parser = create_parser()
        args = parser.parse_args(['--colorscheme_dir', 'this-dir-does-not-exist', 'list'])
        main(args)


def test_status_non_existing():
    with raises(RuntimeError):
        parser = create_parser()
        args = parser.parse_args(['--config_file', 'this-config-does-not-exist', 'status'])
        main(args)


def test_status_existing_configured():
    parser = create_parser()
    args = parser.parse_args(['--config_file', './tests/test-config/alacritty-with-color.yml', 'status'])
    main(args)


def test_status_existing_non_configured():
    parser = create_parser()
    args = parser.parse_args(['--config_file', './tests/test-config/alacritty-without-color.yml', 'status'])
    main(args)


'''
def test_apply():
    parser = create_parser()
    args = parser.parse_args(['apply', 'base16-zenburn'])
    main(args)


def test_toggle():
    parser = create_parser()
    args = parser.parse_args(['toggle'])
    main(args)
'''
