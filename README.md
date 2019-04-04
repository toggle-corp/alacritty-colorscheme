# Alacritty Colorscheme

Change colorscheme of alacritty with ease.

![Usage](https://user-images.githubusercontent.com/4928045/38159826-c451861a-34d0-11e8-979b-34b67027fb87.gif)

To identify the color section in alacritty config, the program uses two markers: ``# color_start`` and ``# color_end``
The markers should be placed before the color section and after the color section by the user.

Example:
```
# color_start
colors:
    # Default colors
    primary:
        background: '0x1e2127'
        foreground: '0xabb2bf'

    # Normal colors
    ...

    # Bright colors
    ...

# color_end
```

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

## Themes

You can get the themes from ``https://github.com/eendroroy/alacritty-theme``

```
# Get themes
git clone https://github.com/eendroroy/alacritty-theme.git ~/alacritty-theme

# List available themes
alacritty-colorscheme -C ~/alacritty-theme/themes -l

# Toggle between the themes
alacritty-colorscheme -C ~/alacritty-theme/themes -T
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

## License

Content of this repo is released under the [Apache License, Version 2.0].

[Apache License, Version 2.0](./LICENSE-APACHE)
