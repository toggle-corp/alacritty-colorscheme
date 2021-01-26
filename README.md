# Alacritty Colorscheme

![PyPI](https://img.shields.io/pypi/v/alacritty-colorscheme) ![PyPI - Downloads](https://img.shields.io/pypi/dm/alacritty-colorscheme)

Change colorscheme of alacritty with ease.

![Usage](https://user-images.githubusercontent.com/4928045/105879854-c7170680-602a-11eb-86d5-d9e89a68f229.gif)

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
    # Create symlink for colors (optional)
    ln -s "$DEST/colors" "$HOME/.config/alacritty/color"
    ```

- You can also get colorschemes from from [eendroroy/alacritty-theme](https://github.com/eendroroy/alacritty-theme)

    ```bash
    REPO=htt#ps://github.com/eendroroy/alacritty-theme.git 
    DEST="$HOME/.eendroroy-colorschemes"
    # Get colorschemes
    git clone $REPO $DEST
    # Create symlink (optional)
    ln -s "$DEST/themes" "$HOME/.config/alacritty/color"
    ```

## Examples 

### bash/zsh aliases

In `.zshrc` or `.bashrc` file:
```bash
LIGHT_COLOR='base16-gruvbox-light-soft.yml'
DARK_COLOR='base16-gruvbox-dark-soft.yml'

alias day="alacritty-colorscheme -V apply $LIGHT_COLOR && reload_nvim"
alias night="alacritty-colorscheme -V apply $DARK_COLOR && reload_nvim"
alias toggle="alacritty-colorscheme -V toggle $LIGHT_COLOR $DARK_COLOR && reload_nvim"
```

### i3wm/sway bindings

In `config` file:
```bash
set $light_color base16-gruvbox-light-soft.yml
set $dark_color base16-gruvbox-dark-soft.yml

# Toggle between light and dark colorschemes
bindsym $mod+Shift+n exec alacritty-colorscheme toggle $light_color $dark_color

# Toggle between all available colorschemes
bindsym $mod+Shift+m exec alacritty-colorscheme toggle

# Get notification with current colorscheme
bindsym $mod+Shift+b exec notify-send "Alacritty Colorscheme" `alacritty-colorscheme status`
```

## FAQ

### How to make vim use same colorscheme as alacritty?

If you are using base16 colorschemes from
[base16-vim](https://github.com/chriskempson/base16-vim) plugin, you can use
the `-V` argument to generate `~/.vimrc_background` file when you change
alacritty colorscheme.

You will need to source this file in your vimrc to load the appropriate
colorscheme in vim.

In your `.vimrc` file:
```vim
if filereadable(expand("~/.vimrc_background"))
  let base16colorspace=256          " Remove this line if not necessary
  source ~/.vimrc_background
endif
```

Now, you simply need to reload your vim configuration after you change the
alacritty colorscheme.

### Can I automatically reload my vim configuration?

If you are using neovim, you can use
[neovim-remote](https://github.com/mhinz/neovim-remote) to reload the nvim
sessions externally.

Install neovim-remote:

```bash
pip install --user neovim-remote
```

Reload colorscheme in all neo-vim sessions using neovim-remote.

```bash
function reload_nvim {
    for SERVER in $(nvr --serverlist); do
        # Just sourcing the code to apply new colorscheme
        nvr --nostart -s -cc "source ~/.vimrc_background" --servername $SERVER &
    done
}
```

## Development

## Running locally

```bash
# Install poetry
pip install --user poetry

git clone https://github.com/toggle-corp/alacritty-colorscheme.git
cd alacritty-colorscheme

poetry install
poetry run python alacritty_colorscheme/cli.py
```

### Installing locally

```bash
pip install --user .
```

## License

Content of this repository is released under the [Apache License, Version 2.0].

[Apache License, Version 2.0](./LICENSE-APACHE)
