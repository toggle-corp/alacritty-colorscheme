# Alacritty Colorscheme

Change colorscheme of alacritty with ease.

![Usage](https://user-images.githubusercontent.com/4928045/38159826-c451861a-34d0-11e8-979b-34b67027fb87.gif)

## Usage

```bash
$ alacritty-colorscheme --help
usage: alacritty-colorscheme [-h]
                             (-s | -l | -a colorscheme | -t colorschemes [colorschemes ...] | -T)
                             [-c configuration file]
                             [-C colorscheme directory]
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
  -c configuration file, --config-file configuration file
                        Path to configuration file
  -C colorscheme directory, --colorscheme-directory colorscheme directory
                        Path to colorscheme directory
```

## Bindings for i3wm

```
# Set program location
set $alacritty_colorscheme ~/.bin/alacritty-colorscheme
# Toggle between light and dark colorscheme
bindsym $mod+Shift+n exec $alacritty_colorscheme -t solarized-light.yml solarized-dark.yml
# Toggle between all available colorscheme
bindsym $mod+Shift+m exec $alacritty_colorscheme -T
# Get notification with current colorscheme
bindsym $mod+Shift+b exec notify-send "Alacritty Colorscheme" `$alacritty_colorscheme -s`
```
