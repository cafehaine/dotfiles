#!/usr/bin/env python3
import json
import subprocess

workspace_names = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

output = json.loads(
    subprocess.run(
        ["swaymsg", "-t", "get_workspaces"], stdout=subprocess.PIPE
    ).stdout.decode()
)
firstOpenWorkspace = 0

for workspace in output:
    if workspace["name"] == workspace_names[firstOpenWorkspace]:
        firstOpenWorkspace += 1

subprocess.run(["swaymsg", "workspace", workspace_names[firstOpenWorkspace]])
