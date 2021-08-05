from os import listdir, environ
from os.path import join
from pynvim import attach


def template_vimrc_background(colorscheme: str) -> str:
    command = (
        f"if !exists('g:colors_name') || g:colors_name != '{colorscheme}'\n"
        f"  colorscheme {colorscheme}\n"
        "endif")
    return command


def _get_all_instances():
    instances = []

    tmpdir = environ.get('TMPDIR', '/tmp')

    folders = [f for f in listdir(tmpdir) if f.startswith('nvim')]
    for folder in folders:
        dc = listdir(join(tmpdir, folder))
        if '0' in dc:
            instances.append(join(tmpdir, folder, '0'))

    return instances


def _reload(instance, colorscheme_file):
    nvim = attach('socket', path=instance)
    nvim.command(f'source {colorscheme_file}')


def reload_neovim_sessions(colorscheme_file):
    instances = _get_all_instances()
    try:
        for instance in instances:
            _reload(instance, colorscheme_file)
    except Exception:
        print('Failed loading colorscheme to nvim')
