# Alacritty Colorscheme

Change colorscheme of alacritty with ease.

![Usage](https://user-images.githubusercontent.com/4928045/38159826-c451861a-34d0-11e8-979b-34b67027fb87.gif)

## Usage

```
usage: alacritty-colorscheme [-h] (-s | -l | -a colorscheme | -t colorschemes [colorschemes ...] | -T) [-r] [-c configuration file] [-C colorscheme directory] [-V]

Change colorscheme of alacritty with ease.

optional arguments:
  -h, --help            show this help message and exit
  -s, --show-applied    Show applied colorscheme
  -l, --list-available  List available colorschemes
  -a colorscheme, --apply colorscheme
                        Apply colorscheme
  -t colorschemes [colorschemes ...], --toggle colorschemes [colorschemes ...]
                        Toggle colorschemes
  -T, --toggle-available
                        Toggle all available colorschemes
  -r, --reverse-toggle  Toggle through colorschemes in reverse order
  -c configuration file, --config-file configuration file
                        Path to configuration file
  -C colorscheme directory, --colorscheme-directory colorscheme directory
                        Path to colorscheme directory
  -V, --base16-vim      Support base16-vim
```

## Installation

You can install it from pip:

```bash
pip install --user alacritty-colorscheme
```

## Running locally

```bash
# Install poetry
pip install --user poetry

# Get program
git clone https://github.com/toggle-corp/alacritty-colorscheme.git

# Run program
cd alacritty-colorscheme
poetry install
poetry run python alacritty_colorscheme/cli.py
```

## Getting themes

You can get themes from [aaron-williamson/base16-alacritty](https://github.com/aaron-williamson/base16-alacritty)

```bash
DEST="$HOME/.aaron-williamson-alacritty-theme"

# Get themes
git clone https://github.com/aaron-williamson/base16-alacritty.git $DEST
```

You can alternatively get themes from from [eendroroy/alacritty-theme](https://github.com/eendroroy/alacritty-theme)

```bash
DEST="$HOME/.eendroroy-alacritty-theme"

# Get themes
git clone https://github.com/eendroroy/alacritty-theme.git $DEST
```

## Synchronizing with vim/neovim

If you are using base16 colorschemes from
[base16-vim](https://github.com/chriskempson/base16-vim), you can use the `-V`
argument to generate `~/.vimrc_background` file when you change alacritty
colorscheme.

You will need to source the file in your vimrc to load the appropriate
colorscheme in vim. Add the following in your vimrc file:

```vim
if filereadable(expand("~/.vimrc_background"))
  let base16colorspace=256          " Remove this line if not necessary
  source ~/.vimrc_background
endif
```

After changing alacritty colorscheme, you need to simply reload your vimrc
configuration.

### Reloading neovim

If you are using neovim, you can use
[neovim-remote](https://github.com/mhinz/neovim-remote) to reload the nvim
sessions externally.

Install neovim-remote:

```bash
pip install --user neovim-remote
```

Reload a neovim session using:

```bash
nvr -cc "source ~/.config/nvim/init.vim"
```

## Example bash/zsh configuration (base16-vim + neovim + neovim-remote)

You can add this example configuration in your .zshrc or .bashrc to switch
between dark and light theme.
This snippet creates two aliases namely: `day`, `night`

```bash
function reload_nvim {
    for SERVER in $(nvr --serverlist); do
        nvr -cc "source ~/.config/nvim/init.vim" --servername $SERVER &
    done
}

COLOR_DIR="$HOME/.aaron-williamson-alacritty-theme/colors"
LIGHT_COLOR='base16-gruvbox-light-soft.yml'
DARK_COLOR='base16-gruvbox-dark-soft.yml'

alias day="alacritty-colorscheme -C $COLOR_DIR -a $LIGHT_COLOR -V && reload_nvim"
alias night="alacritty-colorscheme -C $COLOR_DIR -a $DARK_COLOR -V && reload_nvim"
```

## Example i3wm/sway configuration

```bash
set $color_dir $HOME/.aaron-williamson-alacritty-theme/colors
set $light_color base16-gruvbox-light-soft.yml
set $dark_color base16-gruvbox-dark-soft.yml

# Toggle between light and dark colorscheme
bindsym $mod+Shift+n exec alacritty-colorscheme -C $color_dir -t $light_color $dark_color

# Toggle between all available colorscheme
bindsym $mod+Shift+m exec alacritty-colorscheme -C $color_dir -T

# Get notification with current colorscheme
bindsym $mod+Shift+b exec notify-send "Alacritty Colorscheme" `alacritty-colorscheme -C $color_dir -s`
```

## License

Content of this repository is released under the [Apache License, Version 2.0].

[Apache License, Version 2.0](./LICENSE-APACHE)
