#!/usr/bin/env python3

from tap import Tap
from tempfile import NamedTemporaryFile
from typing import List, Optional, Literal, cast
from os import listdir
from os.path import expanduser, isfile, join

from . import __version__
from .colorscheme import get_applied_colorscheme, get_applicable_colorscheme, replace_colorscheme


class StatusParser(Tap):
    pass


# TODO: filter dark and light backgrounds
class ListParser(Tap):
    pass


class ApplyParser(Tap):
    colorscheme: str

    def configure(self) -> None:
        self.add_argument('colorscheme')


class ToggleParser(Tap):
    colorschemes: List[str] = []
    reverse: bool = False

    def configure(self) -> None:
        self.add_argument('colorschemes')


config_path = join('~', '.config/alacritty/alacritty.yml')
colorscheme_dir = join('~', '.config/alacritty/colors/')


class ArgumentParser(Tap):
    config_file: str = config_path  # Path to alacritty configuration file
    colorscheme_dir: str = colorscheme_dir  # Path to colorscheme directory
    base16_vim: bool = False  # Support base16-vim. Generates .vimrc_background file at home directory
    # version: str  # Version

    def configure(self) -> None:
        self.add_subparsers(help='sub-command help', dest="_subparser_name")
        self.add_subparser('list', ListParser, help='List available colorschemes')
        self.add_subparser('status', StatusParser, help='Show current colorscheme')
        self.add_subparser('toggle', ToggleParser, help='Toggle colorscheme')
        self.add_subparser('apply', ApplyParser, help='Apply colorscheme')

        self.add_argument('-c',
                          '--config_file',
                          metavar='configuration file')

        self.add_argument('-C',
                          '--colorscheme_dir',
                          metavar='colorscheme directory')

        self.add_argument('-V',
                          '--base16_vim')

        self.add_argument('-v',
                          '--version',
                          action='version',
                          version='%(prog)s {version}'.format(version=__version__))


# NOTE: adding '_subparser_naem' to ArgumentParser will add a new argument.
# So, creating this class for type casting purpose only
class HackArgumentParser(ArgumentParser):
    _subparser_name: Literal['list', 'status', 'toggle', 'apply']


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(
        "alacritty-colorscheme",
        description="Change colorscheme of alacritty with ease."
    )

    return parser.parse_args()


# TODO: show only yml files
def get_files_in_directory(path: str) -> Optional[List[str]]:
    expanded_path = expanduser(path)
    try:
        onlyfiles = [f for f in listdir(expanded_path)
                     if isfile(join(expanded_path, f))]
        return sorted(onlyfiles)
    except OSError:
        return None


def main() -> None:
    args = cast(HackArgumentParser, parse_args())

    if args._subparser_name == 'list':
        files = get_files_in_directory(args.colorscheme_dir)
        if files is None:
            print(f'Could not find directory: {args.colorscheme_dir}')
        else:
            for file in files:
                print(file)
    elif args._subparser_name == 'status':
        try:
            colorscheme = get_applied_colorscheme(args.config_file)
            if colorscheme is None:
                print('No colorscheme is applied')
            else:
                print(colorscheme)
        except OSError:
            print(f'Could not find a valid alacritty config file: {args.config_file}')
    elif args._subparser_name == 'toggle':
        try:
            colorscheme = get_applied_colorscheme(args.config_file)
        except OSError:
            print(f'Could not find a valid alacritty config file: {args.config_file}')
            return

        toggleArgs = cast(ToggleParser, args)
        colorschemes = toggleArgs.colorschemes \
            if toggleArgs.colorschemes \
            else get_files_in_directory(args.colorscheme_dir)
        if colorschemes is None:
            print(f'Could not find directory {args.colorscheme_dir}')
        else:
            applicable_colorscheme = get_applicable_colorscheme(
                colorschemes,
                colorscheme,
                toggleArgs.reverse,
            )
            if applicable_colorscheme is None:
                print('There is no applicable colorscheme')
            else:
                colors_path = join(args.colorscheme_dir, applicable_colorscheme)
                replace_colorscheme(colors_path, args.config_file,
                                    applicable_colorscheme, args.base16_vim)
    elif args._subparser_name == 'apply':
        applyArgs = cast(ApplyParser, args)
        colors_path = join(args.colorscheme_dir, applyArgs.colorscheme)
        replace_colorscheme(colors_path, args.config_file,
                            applyArgs.colorscheme, args.base16_vim)
    else:
        args.print_usage()


if __name__ == "__main__":
    main()
