#!/usr/bin/env -S uv run --script
#
# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "psutil==7.1.3",
#     "tomlkit==0.13.3",
# ]
# ///
from os.path import expanduser
from pathlib import Path
from signal import Signals

from psutil import process_iter
from tomlkit import dumps, loads

HELIX_CONFIG_PATH = Path(expanduser("~/.config/helix/config.toml"))

HELIX_DARK_THEME = "adwaita-dark"
HELIX_LIGHT_THEME = "catppuccin_latte"


def switch_theme(theme_name: str) -> None:
    # Edit helix config
    config = loads(HELIX_CONFIG_PATH.read_text())
    config["theme"] = theme_name
    HELIX_CONFIG_PATH.write_text(dumps(config))
    print("Wrote config.")

    # Send SIGUSR1 to all helix processes
    for process in process_iter():
        if process.name() == "helix":
            process.send_signal(Signals.SIGUSR1)
            print("Sent SIGUSR1 to helix instance", process.pid)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("theme", choices=("light", "dark"))
    args = parser.parse_args()

    if args.theme == "light":
        switch_theme(HELIX_LIGHT_THEME)
    else:
        switch_theme(HELIX_DARK_THEME)
