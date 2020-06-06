#!/usr/bin/env python3

import argparse
import pprint
import re
import sys
import tempfile
import typing
from os import listdir, replace, unlink
from os.path import expanduser, isfile, join, splitext
from shutil import copyfile

from ruamel.yaml import YAML
from ruamel.yaml.comments import Comment
from ruamel.yaml.error import CommentMark
from ruamel.yaml.tokens import CommentToken

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)

def parse_args():
    config_path = join('~', '.config/alacritty/alacritty.yml')
    colorscheme_dir = join('~', '.config/alacritty/colors/')

    parser = argparse.ArgumentParser(
        "alacritty-colorscheme",
        description="Change colorscheme of alacritty with ease."
    )

    optype = parser.add_mutually_exclusive_group(required=True)

    optype.add_argument('-s',
                        '--show-applied',
                        dest='show_applied_colorscheme',
                        help='Show applied colorscheme',
                        action='store_const',
                        const=True)

    optype.add_argument('-l',
                        '--list-available',
                        dest='list_available_colorschemes',
                        help='List available colorschemes',
                        action='store_const',
                        const=True)

    optype.add_argument('-a',
                        '--apply',
                        dest='colorscheme',
                        help='Apply colorscheme',
                        metavar='colorscheme',
                        type=str)

    optype.add_argument('-t',
                        '--toggle',
                        dest='colorschemes',
                        help='Toggle colorschemes',
                        metavar='colorschemes',
                        nargs='+')

    optype.add_argument('-T',
                        '--toggle-available',
                        dest='toggle_available',
                        help='Toggle all available colorschemes',
                        action='store_const',
                        const=True)

    parser.add_argument('-c',
                        '--config-file',
                        dest='config_file',
                        help='Path to configuration file',
                        metavar='configuration file',
                        type=str,
                        default=config_path,
                        required=False)

    parser.add_argument('-C',
                        '--colorscheme-directory',
                        dest='colorscheme_dir',
                        help='Path to colorscheme directory',
                        metavar='colorscheme directory',
                        type=str,
                        default=colorscheme_dir,
                        required=False)

    parser.add_argument('-V',
                        '--base16-vim',
                        dest='base16_vim',
                        help='Support base16-vim',
                        action='store_const',
                        const=True)
    return parser.parse_args()

def get_files_in_directory(path: str) -> typing.List[str]:
    expanded_path = expanduser(path)
    onlyfiles = [f for f in (listdir(expanded_path)) if isfile(join(expanded_path, f))]
    return sorted(onlyfiles)

def generate_vimrc_background(colorscheme: str) -> str:
    command = (
        f"if !exists('g:colors_name') || g:colors_name != '{colorscheme}'\n"
        f"  colorscheme {colorscheme}\n"
        "endif")
    return command

# function to identify if a given yaml.Comment internally has at least one comment
def has_comment_token(colors_comment: Comment) -> bool:
    if not colors_comment or len(colors_comment) < 2:
        return False

    comment_tokens = colors_comment[1]
    return comment_tokens and len(comment_tokens) >= 1

def get_applied_colorscheme(config_path: str) -> typing.Optional[str]:
    try:
        with open(expanduser(config_path), 'r') as config_file:
            config_yaml = yaml.load(config_file)

            if not has_comment_token(config_yaml['colors'].ca.comment):
                return None

            comment_match = re.match(
                r"#\s*COLORSCHEME:\s*(.*)\s*\n",
                config_yaml['colors'].ca.comment[1][0].value,
            )

            if not comment_match:
                return None

            comment_groups = comment_match.groups()
            return comment_groups[0]
    except Exception as e:
        print(e)
        return None

def replace_colorscheme(colors_path: str, config_path: str, colorscheme: str, base16_vim: bool):
    with open(expanduser(config_path), 'r') as config_file,\
            open(expanduser(colors_path), 'r') as color_file,\
            tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        config_yaml = yaml.load(config_file)
        colors_yaml = yaml.load(color_file)

        # NOTE: update method doesn't read the first comment
        config_yaml['colors'].update(colors_yaml['colors'])

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
            config_yaml['colors'].ca.comment[1].extend(colors_yaml['colors'].ca.comment[1])

        # NOTE: not directly writing to config_file as it causes multiple reload during write
        tmp_file_path = tmp_file.name
        yaml.dump(config_yaml, tmp_file)

    copyfile(tmp_file_path, expanduser(config_path));
    unlink(tmp_file_path)

    if base16_vim:
        vimrc_background_path = join('~', '.vimrc_background')
        with open(expanduser(vimrc_background_path), 'w') as vimrc_background_file:
            colorscheme_no_extension = splitext(colorscheme)[0]
            vimrc_background_content = generate_vimrc_background(
                colorscheme_no_extension
            )
            vimrc_background_file.write(vimrc_background_content)

def main():
    args = parse_args()

    if args.list_available_colorschemes:
        files = get_files_in_directory(args.colorscheme_dir)
        for file in files:
            print(file)
    elif args.show_applied_colorscheme:
        colorscheme = get_applied_colorscheme(args.config_file)
        print(colorscheme)
    elif args.colorscheme:
        colors_path = join(args.colorscheme_dir, args.colorscheme)
        replace_colorscheme(colors_path, args.config_file,
                            args.colorscheme, args.base16_vim)
    elif args.colorschemes:
        colorscheme = get_applied_colorscheme(args.config_file)
        realindex = args.colorschemes.index(colorscheme)\
            if colorscheme in args.colorschemes else -1
        index = (realindex + 1) % len(args.colorschemes)
        applicable_colorscheme = args.colorschemes[index]

        colors_path = join(args.colorscheme_dir, applicable_colorscheme)
        replace_colorscheme(colors_path, args.config_file,
                            applicable_colorscheme, args.base16_vim)
    elif args.toggle_available:
        colorschemes = get_files_in_directory(args.colorscheme_dir)
        colorscheme = get_applied_colorscheme(args.config_file)
        realindex = colorschemes.index(colorscheme)\
            if colorscheme in colorschemes else -1
        index = (realindex + 1) % len(colorschemes)
        applicable_colorscheme = colorschemes[index]

        colors_path = join(args.colorscheme_dir, applicable_colorscheme)
        replace_colorscheme(colors_path, args.config_file,
                            applicable_colorscheme, args.base16_vim)


if __name__ == "__main__":
    main()
