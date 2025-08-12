#!/usr/bin/env python3
# pyright: strict
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
import asyncio
from enum import Enum, IntEnum
import json
import logging
from pathlib import Path
import os
import re
import shutil
import signal
import subprocess
import sys
import traceback
from types import FrameType

LOGGER = logging.getLogger(__name__)

SWAYSOCK = os.getenv("SWAYSOCK", None)
assert SWAYSOCK is not None, "Not running in Sway!"
SWAYSOCK_PATH = Path(SWAYSOCK)
filename = SWAYSOCK_PATH.parts[-1]
sock_filename = "sway-rotate" + filename.removeprefix("sway-ipc")
SOCK_PATH = SWAYSOCK_PATH.parent / sock_filename


class Command(IntEnum):
    DISABLE = 0
    ENABLE = 1
    TOGGLE = 2
    DISABLE_HARDWARE = 3


class Orientation(Enum):
    UNSET = "unset"
    NORMAL = "normal"
    LEFT_UP = "left-up"
    RIGHT_UP = "right-up"
    BOTTOM_UP = "bottom-up"


async def rotate_screen(output_name: str, orientation: Orientation):
    assert (
        orientation != Orientation.UNSET
    ), "Requested rotation of screen to orientation 'UNSET'!"
    LOGGER.info("Rotating screen %r to orientation %r", output_name, orientation)
    match orientation:
        case Orientation.NORMAL:
            angle = 0
        case Orientation.LEFT_UP:
            angle = 270
        case Orientation.RIGHT_UP:
            angle = 90
        case Orientation.BOTTOM_UP:
            angle = 180
    process = await asyncio.create_subprocess_exec(
        "swaymsg", "output", output_name, "transform", str(angle)
    )
    assert await process.wait() == 0


async def status(args: Namespace) -> int:
    assert shutil.which(
        "monitor-sensor"
    ), "Could not find 'monitor-sensor'. It might be packaged as 'iio-sensor-proxy'."

    # Translate SIGTERMS to SIGINTS (waybar sends SIGTERMS when stopping)
    def handler(signal: int, frame: FrameType | None):
        raise KeyboardInterrupt()

    signal.signal(signal.SIGTERM, handler)

    event_queue: asyncio.Queue[Command | Orientation] = asyncio.Queue()

    async def on_client_connected(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """Handle commands."""
        raw_command = await reader.read(1)
        try:
            command = Command(int.from_bytes(raw_command))
            await event_queue.put(command)
        except Exception:
            print(
                f"Received invalid command from client: {raw_command}",
                file=sys.stderr,
            )
            traceback.print_exc(file=sys.stderr)
        finally:
            writer.close()

    if SOCK_PATH.exists():
        print(
            "An instance of 'sway_rotate.py status' is already running!",
            file=sys.stderr,
        )
        print(
            "If you are certain another instance isn't running, remove the following file:",
            SOCK_PATH,
            file=sys.stderr,
        )
        return 1

    monitor_sensor = await asyncio.create_subprocess_exec(
        "monitor-sensor", "--accel", stdout=subprocess.PIPE
    )

    async def read_orientation():
        """Handle orientation changes."""
        assert monitor_sensor.stdout is not None

        async for raw_line in monitor_sensor.stdout:
            line = raw_line.rstrip(b"\r\n").decode()
            match = re.match(
                r"^(?:"
                r"    Accelerometer orientation changed: (?P<orientation>.*)"
                r"|"
                r"=== Has accelerometer \(orientation: (?P<initial_orientation>.*?), .*\)"
                r")$",
                line,
            )
            if match is not None:
                if match["orientation"] is not None:
                    raw_orientation = match["orientation"]
                else:
                    raw_orientation = match["initial_orientation"]
                try:
                    orientation = Orientation(raw_orientation)
                except ValueError:
                    LOGGER.warning("Unknow orientation: %r", raw_orientation)
                    continue
                await event_queue.put(orientation)
            else:
                LOGGER.debug("Ignored line %r", line)

    # TODO save in .cache?
    enabled = True
    # TODO determine by reading current screen disposition?
    orientation = Orientation.UNSET
    server = await asyncio.start_unix_server(on_client_connected, SOCK_PATH)
    async with server:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(read_orientation())
            while True:
                output = {
                    "text": args.enabled_text if enabled else args.disabled_text,
                    "tooltip": f"Automatic rotation enabled: {enabled}\nOrientation: {orientation.value}",
                }
                print(json.dumps(output), flush=True)
                event = await event_queue.get()
                LOGGER.debug("Handling event %r", event)
                match event:
                    case Command.DISABLE:
                        enabled = False
                        LOGGER.debug("Automatic rotation disabled")
                    case Command.ENABLE:
                        enabled = True
                        LOGGER.debug("Automatic rotation enabled")
                        await rotate_screen(args.output_name, orientation)
                        LOGGER.debug(
                            "Rotated screen to orientation %s", orientation.value
                        )
                    case Command.TOGGLE:
                        enabled = not enabled
                        LOGGER.debug(
                            "Automatic rotation %s",
                            "enabled" if enabled else "disabled",
                        )
                    case Command.DISABLE_HARDWARE:
                        enabled = False
                        if args.hardware_disabled_orientation != Orientation.UNSET:
                            await rotate_screen(
                                args.output_name, args.hardware_disabled_orientation
                            )
                        LOGGER.debug("Automatic rotation disabled (hardware)")
                    case requested_orientation:
                        orientation = requested_orientation
                        if enabled:
                            await rotate_screen(args.output_name, orientation)
                            LOGGER.debug(
                                "Rotated screen to orientation %s",
                                orientation.value,
                            )
                        else:
                            LOGGER.debug(
                                "Stored desired orientation %s", orientation.value
                            )


async def send_command(command: Command) -> int:
    if not SOCK_PATH.exists():
        print("No instance of 'sway_rotate.py status' found running.", file=sys.stderr)
        return 1
    _, writer = await asyncio.open_unix_connection(SOCK_PATH)
    writer.write(command.value.to_bytes())
    await writer.drain()
    writer.close()
    return 0


async def disable(args: Namespace) -> int:
    if args.hardware:
        return await send_command(Command.DISABLE_HARDWARE)
    else:
        return await send_command(Command.DISABLE)


async def enable(_: Namespace) -> int:
    return await send_command(Command.ENABLE)


async def toggle(_: Namespace) -> int:
    return await send_command(Command.TOGGLE)


if __name__ == "__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity level (can be specified up to 2 times)",
    )
    subparsers = parser.add_subparsers(required=True)

    status_subparser = subparsers.add_parser(
        "status",
        help="Run as a waybar status. This is the command that will actually rotate the screen.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    status_subparser.set_defaults(callback=status)
    status_subparser.add_argument(
        "--enabled-text",
        default="auto-rotate ON",
        help="The text that is printed out when automatic rotation is enabled.",
    )
    status_subparser.add_argument(
        "--disabled-text",
        default="auto-rotate OFF",
        help="The text that is printed out when automatic rotation is disabled.",
    )
    status_subparser.add_argument(
        "--hardware-disabled-orientation",
        choices=[orientation.value for orientation in Orientation],
        type=Orientation,
        default=Orientation.NORMAL.value,
        help="The orientation that will be applied when receiving a 'disable' command from a hardware switch.",
    )
    status_subparser.add_argument(
        "--output-name",
        default="*",
        help="The screen to rotate. See 'man 5 sway-outputs' for how to select outputs.",
    )

    disable_subparser = subparsers.add_parser(
        "disable",
        help="Disable the automatic rotation.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    disable_subparser.set_defaults(callback=disable)
    disable_subparser.add_argument(
        "--hardware",
        action="store_true",
        help="If the disable command is issued because of a hardware switch. This is used to force an orientation.",
    )

    enable_subparser = subparsers.add_parser(
        "enable",
        help="Enable the automatic rotation",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    enable_subparser.set_defaults(callback=enable)

    toggle_subparser = subparsers.add_parser(
        "toggle",
        help="Toggle the current status",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    toggle_subparser.set_defaults(callback=toggle)

    args = parser.parse_args()

    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose == 2:
        level = logging.DEBUG
    else:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(module)s+%(lineno)d: %(message)s",
    )

    sys.exit(asyncio.run(args.callback(args)))
