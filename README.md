# Alacritty Colorscheme

![PyPI](https://img.shields.io/pypi/v/alacritty-colorscheme) ![PyPI - Downloads](https://img.shields.io/pypi/dm/alacritty-colorscheme)

Change colorscheme of alacritty with ease.

![Usage](https://user-images.githubusercontent.com/4928045/106160031-8267a880-61ad-11eb-9acf-b9d5cd5de3e4.gif)

## Installation

You can install alacritty-colorscheme using pip:

```bash
pip install --user alacritty-colorscheme
```

## Usage

```
usage: alacritty-colorscheme [-c configuration file] [-C colorscheme directory] [-V] [-h]
                             {list,status,toggle,apply} ...
```

## Getting colorschemes

- You can get colorschemes from [aaron-williamson/base16-alacritty](https://github.com/aaron-williamson/base16-alacritty)

    ```bash
    REPO="https://github.com/aaron-williamson/base16-alacritty.git"
    DEST="$HOME/.aarors-williamson-colorschemes"

    # Get colorschemes 
    git clone $REPO $DEST
    # Create symlink at default colors location (optional)
    ln -s "$DEST/colors" "$HOME/.config/alacritty/colors"
    ```

- You can also get colorschemes from from [eendroroy/alacritty-theme](https://github.com/eendroroy/alacritty-theme)

    ```bash
    REPO=https://github.com/eendroroy/alacritty-theme.git
    DEST="$HOME/.eendroroy-colorschemes"
    # Get colorschemes
    git clone $REPO $DEST
    # Create symlink at default colors location (optional)
    ln -s "$DEST/themes" "$HOME/.config/alacritty/colors"
    ```

## Sync with vim/neo-vim

If you are using base16 colorschemes from
[base16-vim](https://github.com/chriskempson/base16-vim) plugin, you can use
the `-V` argument to automatically generate `~/.vimrc_background` file when you
change alacritty colorscheme. You will need to source this file in your vimrc
to load the same colorscheme in vim.

Add this in your `.vimrc` file:

```vim
if filereadable(expand("~/.vimrc_background"))
  let base16colorspace=256          " Remove this line if not necessary
  source ~/.vimrc_background
endif
```

When you change your alacritty colorscheme, you simply need to source
`~/.vimrc_background` or your `vimrc`.
If you are a neo-vim user, `~/.vimrc_background` will be automatically sourced.

## Examples

### bash/zsh aliases

Add this in your `.zshrc` or `.bashrc` file:

```bash
LIGHT_COLOR='base16-gruvbox-light-soft.yml'
DARK_COLOR='base16-gruvbox-dark-soft.yml'

alias day="alacritty-colorscheme -V apply $LIGHT_COLOR"
alias night="alacritty-colorscheme -V apply $DARK_COLOR"
alias toggle="alacritty-colorscheme -V toggle $LIGHT_COLOR $DARK_COLOR"
```

### i3wm/sway bindings

Add this in your i3 `config` file:

```bash
set $light_color base16-gruvbox-light-soft.yml
set $dark_color base16-gruvbox-dark-soft.yml

# Toggle between light and dark colorschemes
bindsym $mod+Shift+n exec alacritty-colorscheme -V toggle $light_color $dark_color

# Toggle between all available colorschemes
bindsym $mod+Shift+m exec alacritty-colorscheme -V toggle

# Get notification with current colorscheme
bindsym $mod+Shift+b exec notify-send "Alacritty Colorscheme" `alacritty-colorscheme status`
```

## Development

### Running locally

```bash
pip install --user poetry

git clone https://github.com/toggle-corp/alacritty-colorscheme.git
cd alacritty-colorscheme

poetry install
poetry run python -m alacritty_colorscheme.cli
```

### Installing locally

```bash
pip install --user .
```

## License

Content of this repository is released under the [Apache License, Version 2.0].

[Apache License, Version 2.0](./LICENSE-APACHE)
