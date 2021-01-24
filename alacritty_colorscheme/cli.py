#!/usr/bin/env python3

from tap import Tap
from re import match
from tempfile import NamedTemporaryFile
from typing import List, Optional, Literal, cast
from os import listdir, unlink
from os.path import expanduser, isfile, join, splitext
from shutil import copyfile
from ruamel.yaml import YAML
from ruamel.yaml.error import CommentMark
from ruamel.yaml.tokens import CommentToken

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

config_path = join('~', '.config/alacritty/alacritty.yml')
colorscheme_dir = join('~', '.config/alacritty/colors/')


class ApplyParser(Tap):
    colorscheme: str

    def configure(self) -> None:
        self.add_argument('colorscheme')


# TODO: filter dark and light backgrounds
class ListParser(Tap):
    pass


class StatusParser(Tap):
    pass


class ToggleParser(Tap):
    colorschemes: List[str] = []
    reverse: bool = False

    def configure(self) -> None:
        self.add_argument('colorschemes')


class SimpleArgumentParser(Tap):
    config_file: str = config_path  # Path to alacritty configuration file
    colorscheme_dir: str = colorscheme_dir  # Path to colorscheme directory
    base16_vim: bool = False  # Support base16-vim. Generates .vimrc_background file at home directory

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


# NOTE: adding this to SimpleArgumentParser will add a new argument.
# Creating this class for casting purpose only
class HackArgumentParser(SimpleArgumentParser):
    _subparser_name: Literal['list', 'status', 'toggle', 'apply']


def parse_args() -> SimpleArgumentParser:
    parser = SimpleArgumentParser(
        "alacritty-colorscheme",
        description="Change colorscheme of alacritty with ease."
    )

    return parser.parse_args()


# TODO: show only yml files
def get_files_in_directory(path: str) -> Optional[List[str]]:
    expanded_path = expanduser(path)
    try:
        onlyfiles = [f for f in (listdir(expanded_path))
                     if isfile(join(expanded_path, f))]
        return sorted(onlyfiles)
    except OSError:
        return None


def template_vimrc_background(colorscheme: str) -> str:
    command = (
        f"if !exists('g:colors_name') || g:colors_name != '{colorscheme}'\n"
        f"  colorscheme {colorscheme}\n"
        "endif")
    return command


# NOTE: function to identify if a given `yaml.Comment` internally has
# at least one comment
def has_comment_token(colors_comment: List) -> bool:
    if not colors_comment or len(colors_comment) < 2:
        return False

    comment_tokens = colors_comment[1]
    return comment_tokens and len(comment_tokens) >= 1


def get_applied_colorscheme(config_path: str) -> Optional[str]:
    with open(expanduser(config_path), 'r') as config_file:
        config_yaml = yaml.load(config_file)

    if not has_comment_token(config_yaml['colors'].ca.comment):
        return None

    comment_match = match(
        r"#\s*COLORSCHEME:\s*(.*)\s*\n",
        config_yaml['colors'].ca.comment[1][0].value,
    )

    if not comment_match:
        return None

    comment_groups = comment_match.groups()
    return comment_groups[0]


def replace_colorscheme(
    colors_path: str,
    config_path: str,
    colorscheme: str,
    base16_vim: bool,
) -> None:
    try:
        with open(expanduser(config_path), 'r') as config_file:
            config_yaml = yaml.load(config_file)
    except OSError:
        print(f'Could not find a valid alacritty config file: {config_path}')
        return

    try:
        with open(expanduser(colors_path), 'r') as color_file:
            colors_yaml = yaml.load(color_file)
    except OSError:
        print(f'Could not find a valid alacritty colorscheme file: {colors_path}')
        return

    try:
        # NOTE: update method doesn't read the first comment
        config_yaml['colors'].update(colors_yaml['colors'])
    except KeyError:
        config_yaml['colors'] = colors_yaml['colors']

    new_comment_token = CommentToken(
        f'# COLORSCHEME: {colorscheme}\n',
        CommentMark(2),
        None,
    )

    if has_comment_token(config_yaml['colors'].ca.comment):
        # removing all comments for colors in config_file
        while len(config_yaml['colors'].ca.comment[1]) > 0:
            config_yaml['colors'].ca.comment[1].pop()

        # adding current colorscheme name in comment
        config_yaml['colors'].ca.comment[1].append(new_comment_token)
    else:
        # adding current colorscheme name in comment
        config_yaml['colors'].ca.comment = [None, [new_comment_token]]

    # adding all comments for colors from colors_file
    if has_comment_token(colors_yaml['colors'].ca.comment):
        config_yaml['colors'].ca.comment[1].extend(
            colors_yaml['colors'].ca.comment[1]
        )

    try:
        with NamedTemporaryFile(delete=False) as tmp_file:
            # NOTE: not directly writing to config_file as it causes
            # multiple reload during write
            tmp_file_path = tmp_file.name
            yaml.dump(config_yaml, tmp_file)
            copyfile(tmp_file_path, expanduser(config_path))
            unlink(tmp_file_path)
    except OSError:
        print(f'Could not modify alacritty config file: {config_path}')
        return

    if base16_vim:
        vimrc_background_path = join('~', '.vimrc_background')
        try:
            with open(expanduser(vimrc_background_path), 'w') as vimrc_background_file:
                colorscheme_no_extension = splitext(colorscheme)[0]
                vimrc_background_content = template_vimrc_background(
                    colorscheme_no_extension
                )
                vimrc_background_file.write(vimrc_background_content)
        except OSError:
            print(f'Could not save file: {vimrc_background_path}')
            return


def get_applicable_colorscheme(
    colorschemes: List[str],
    colorscheme: Optional[str],
    reverse_toggle: bool
) -> Optional[str]:
    if colorscheme is None:
        index = 0
    else:
        try:
            original_index = colorschemes.index(colorscheme)
            diff = - 1 if reverse_toggle else 1
            index = (original_index + diff) % len(colorschemes)
        except ValueError:
            index = 0

    try:
        return colorschemes[index]
    except IndexError:
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
