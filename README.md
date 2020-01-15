# My dotfiles
## Introduction
These are the config files that I share between all of my computers (at least 5
different machines use them). These dotfiles configure anything from the desktop
environment, to text editors, to media players…

You might find some interesting configs here and there, but most of it is pretty
basic.

## List of requirements
- Desktop environment
  - Sway − The window manager
  - Waybar − A fancy status bar
  - wallutils − Utilities to set the wallpaper
  - swaylock − To lock a session
  - mako − A notification daemo like dunst
  - redshift-wayland-git − redshift with support for sway
  - wl-copy − to set the clipboard from command line
  - clipman − a clipboard manager
  - pactl − To change the volume levels
  - mpc − To control mpd and have some music
  - grim and slurp − to take screenshots
  - kanshi - to setup the screen layouts I use
- GUI apps
  - firefox-developer-edition − Get firefox.
  - imv − Like feh, but for wayland
  - qterminal − a nice terminal with support for ligatures
  - thunar − A lightweight file manager
  - albert − A launcher similar to apple's spotlight
  - mpv − imo the best video player out there
- CLI apps
  - bash/readline
  - vim
  - top
  - curl
  - youtube-dl
  - pacman − (BTW I use arch)
  - yay − a great aur helper

## Setup

### Git clone

```bash
todo
```

### Vim setup

You'll first need to install Vundle:
```bash
git clone https://github.com/VundleVim/Vundle.vim ~/.vim/bundle/Vundle.vim
```
Then install the pre-configured plugins in vim with this command:

WARNING: This will take a long time! (YouCompleteMe is quite big)

```
:PluginInstall
```

Then finalize the setup of YouCompleteMe

```bash
cd ~/.vim/bundle/youcompleteme/
# I'm using --no-regex since it requires something that I don't usually install on my archlinux setups.
python3 install.py --no-regex
```

## License
These config files/small scripts are released under the unlicense. Basically you
can do pretty much anything, without requiring any attribution. Check the
LICENSE file for more info.
