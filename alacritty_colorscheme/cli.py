#!/usr/bin/env python3

import argparse
import re
from os import listdir
from os.path import expanduser, isfile, join

COLORSCHEME_START = '# color_start\n'
COLORSCHEME_END = '# color_end\n'
HOME = expanduser("~")


def parse():
    config_path = join(HOME, '.config/alacritty/alacritty.yml')
    colorscheme_dir = join(HOME, '.config/alacritty/colors/')

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

    return parser.parse_args()


def get_applied_colorscheme(config_path):
    try:
        start_index = -1
        with open(config_path, 'r') as config_file:
            config_lines = config_file.readlines()
            for i, line in enumerate(config_lines):
                if line == COLORSCHEME_START:
                    start_index = i
                    break
        if start_index < 0:
            return None

        colorscheme_line = config_lines[start_index+1]
        colorscheme_re = re.search('# (.*)\s*', colorscheme_line)
        if colorscheme_re:
            return colorscheme_re.group(1)
        return None
    except Exception as e:
        print(e)
        return None


def get_files_in_directory(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    return sorted(onlyfiles)


def replace_colorscheme(colors_path, config_path, colorscheme):
    try:
        with open(config_path, 'r+') as config_file,\
                open(colors_path, 'r') as color_file:
            config_lines = config_file.readlines()
            color_lines = color_file.readlines()

            start_index = 0
            end_index = 0
            for i, line in enumerate(config_lines):
                if line == COLORSCHEME_START:
                    start_index = i
                elif line == COLORSCHEME_END:
                    # NOTE: Possibly break after end_index
                    end_index = i

            if start_index >= end_index:
                print('Bad configuration file.')
                return

            new_lines = (
                config_lines[:start_index + 1]
                # Add currently applied colorscheme name
                + ['# ' + colorscheme + '\n']
                + color_lines
                + ['\n']
                + config_lines[end_index:]
            )

            config_file.seek(0)
            config_file.writelines(new_lines)
            config_file.truncate()
    except Exception as e:
        print(e)


def main():
    args = parse()

    if args.list_available_colorschemes:
        files = get_files_in_directory(args.colorscheme_dir)
        for file in files:
            print(file)
    if args.show_applied_colorscheme:
        colorscheme = get_applied_colorscheme(args.config_file)
        print(colorscheme)
    elif args.colorschemes:
        colorscheme = get_applied_colorscheme(args.config_file)
        realindex = args.colorschemes.index(colorscheme)\
            if colorscheme in args.colorschemes else -1
        index = (realindex + 1) % len(args.colorschemes)
        applicable_colorscheme = args.colorschemes[index]

        colors_path = join(args.colorscheme_dir, applicable_colorscheme)
        replace_colorscheme(colors_path, args.config_file,
                            applicable_colorscheme)
    elif args.toggle_available:
        colorschemes = get_files_in_directory(args.colorscheme_dir)
        colorscheme = get_applied_colorscheme(args.config_file)
        realindex = colorschemes.index(colorscheme)\
            if colorscheme in colorschemes else -1
        index = (realindex + 1) % len(colorschemes)
        applicable_colorscheme = colorschemes[index]

        colors_path = join(args.colorscheme_dir, applicable_colorscheme)
        replace_colorscheme(colors_path, args.config_file,
                            applicable_colorscheme)
    elif args.colorscheme:
        colors_path = join(args.colorscheme_dir, args.colorscheme)
        replace_colorscheme(colors_path, args.config_file, args.colorscheme)


if __name__ == "__main__":
    main()
