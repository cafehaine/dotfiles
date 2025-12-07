#!/usr/bin/env python3
from dataclasses import dataclass
import json
import subprocess

WORKSPACE_NAMES = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


@dataclass
class Workspace:
    name: str
    focused: bool
    output: str
    empty: bool


def get_workspaces() -> list[Workspace]:
    data = json.loads(
        subprocess.run(
            ["swaymsg", "-t", "get_workspaces"], stdout=subprocess.PIPE
        ).stdout.decode()
    )
    output = []
    for obj in data:
        output.append(
            Workspace(
                obj["name"],
                obj["focused"],
                obj["output"],
                obj["representation"] == None,
            )
        )

    return output


def get_workspaces_available_for_output(
    ws_by_name: dict[str, Workspace], focused_ws: Workspace
) -> list[str]:
    workspaces_available_for_output: list[str] = []
    for name in WORKSPACE_NAMES:
        # Don't include workspaces on other outputs
        if name in ws_by_name and ws_by_name[name].output != focused_ws.output:
            continue

        # Don't include empty workspaces if current workspace is empty
        if focused_ws.empty and name not in ws_by_name:
            continue

        workspaces_available_for_output.append(name)

    return workspaces_available_for_output


def switch_ws(ws_name: str) -> None:
    subprocess.run(["swaymsg", "workspace", ws_name], check=True)


def next_ws():
    """
    Focus the next workspace on the focused screen.

    Creates a new workspace if the next workspace isn't contiguous.

    If the current workspace is empty, switch to the next one even if not
    contiguous.
    """
    opened_workspaces = get_workspaces()
    focused_ws = [ws for ws in opened_workspaces if ws.focused][0]
    ws_by_name = {ws.name: ws for ws in opened_workspaces}

    workspaces_available_for_output = get_workspaces_available_for_output(
        ws_by_name, focused_ws
    )

    current_index = workspaces_available_for_output.index(focused_ws.name)
    new_index = (current_index + 1) % len(workspaces_available_for_output)

    switch_ws(workspaces_available_for_output[new_index])


def prev_ws():
    """
    Focus the previous workspace on the focused screen.

    Creates a new workspace if the previous workspace isn't contiguous.

    If the current workspace is empty, switch to the previous one even if not
    contiguous.
    """
    opened_workspaces = get_workspaces()
    focused_ws = [ws for ws in opened_workspaces if ws.focused][0]
    ws_by_name = {ws.name: ws for ws in opened_workspaces}

    workspaces_available_for_output = get_workspaces_available_for_output(
        ws_by_name, focused_ws
    )

    current_index = workspaces_available_for_output.index(focused_ws.name)
    new_index = current_index - 1

    switch_ws(workspaces_available_for_output[new_index])


def new_ws():
    """Creates a new workspace."""
    opened_workspace_names = set(workspace.name for workspace in get_workspaces())

    for workspace_name in WORKSPACE_NAMES:
        if workspace_name not in opened_workspace_names:
            subprocess.run(["swaymsg", "workspace", workspace_name], check=True)
            return


if __name__ == "__main__":
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(title="action", required=True)

    next_parser = subparsers.add_parser("next")
    next_parser.set_defaults(callback=next_ws)

    prev_parser = subparsers.add_parser("prev")
    prev_parser.set_defaults(callback=prev_ws)

    new_parser = subparsers.add_parser("new")
    new_parser.set_defaults(callback=new_ws)

    args = parser.parse_args()
    args.callback()
