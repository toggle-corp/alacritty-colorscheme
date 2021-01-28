from re import match
from tempfile import NamedTemporaryFile
from typing import List, Optional
from os import unlink
from os.path import expanduser, join, splitext
from shutil import copyfile
from ruamel.yaml import YAML
from ruamel.yaml.error import CommentMark
from ruamel.yaml.tokens import CommentToken

from .vim import template_vimrc_background, reload_neovim_sessions

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


# NOTE: function to identify if a given `yaml.Comment` internally has
# at least one comment
def _has_comment_token(colors_comment: List) -> bool:
    if not colors_comment or len(colors_comment) < 2:
        return False

    comment_tokens = colors_comment[1]
    return comment_tokens and len(comment_tokens) >= 1


def get_applied_colorscheme(config_path: str) -> Optional[str]:
    with open(expanduser(config_path), 'r') as config_file:
        config_yaml = yaml.load(config_file)

    if not _has_comment_token(config_yaml['colors'].ca.comment):
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

    if _has_comment_token(config_yaml['colors'].ca.comment):
        # removing all comments for colors in config_file
        while len(config_yaml['colors'].ca.comment[1]) > 0:
            config_yaml['colors'].ca.comment[1].pop()

        # adding current colorscheme name in comment
        config_yaml['colors'].ca.comment[1].append(new_comment_token)
    else:
        # adding current colorscheme name in comment
        config_yaml['colors'].ca.comment = [None, [new_comment_token]]

    # adding all comments for colors from colors_file
    if _has_comment_token(colors_yaml['colors'].ca.comment):
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

        reload_neovim_sessions(vimrc_background_path)


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
