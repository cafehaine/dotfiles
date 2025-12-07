#!/usr/bin/env python3
import subprocess


def set_color_scheme(scheme: str):
    subprocess.run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.interface",
            "color-scheme",
            scheme,
        ],
        check=True,
    )


if __name__ == "__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("theme", choices=("light", "dark"))
    args = parser.parse_args()

    if args.theme == "light":
        set_color_scheme("prefer-light")
    else:
        set_color_scheme("prefer-dark")
