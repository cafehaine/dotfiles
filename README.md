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
  - swaylock − To lock a session
  - wl-copy − to set the clipboard from command line
  - pactl − To change the volume levels
  - mpc − To control mpd and have some music
  - grim and slurp − to take screenshots
  - kanshi - to setup the screen layouts I use
- GUI apps
  - firefox − Get firefox.
  - ghostty − a nice terminal with support for ligatures
  - thunar − A lightweight file manager
  - albert − A launcher similar to apple's spotlight
  - mpv − imo the best video player out there
- CLI apps
  - top
  - curl
  - youtube-dl
  - pacman − (BTW I use arch)

## Setup

### Git clone

```bash
git init
git remote add origin https://github.com/cafehaine/dotfiles
git fetch
git checkout -t origin/main
# Will list confilcting files if any, backup them and remove them
```

## License
These config files/small scripts are released under the unlicense. Basically you
can do pretty much anything, without requiring any attribution. Check the
LICENSE file for more info.
