from xonsh.built_ins import events

# List of blacklisted prefixes for commands
_NOTIF_BLACKLIST = (
    "vim",
    "man",
    "top",
)

# Minimum duration of execution for notifications
_NOTIF_LONG_THRESHOLD = 120

@events.on_postcommand
def _long_cmd_notif(cmd, rtn, out, ts):
    """
    Play a sound and show a notification when a long command is completed.
    """
    start, finish = ts
    length = finish-start

    if cmd.startswith(_NOTIF_BLACKLIST):
        return

    # I should probably use "completion-fail" and "completion-sucess", hovewer
    # those sounds look to be missing on my system.

    if length > _NOTIF_LONG_THRESHOLD:
        if rtn == 0:
            notify-send --icon=dialog-information-symbolic "Command succeeded" @(cmd)
            canberra-gtk-play -i dialog-information
        else:
            notify-send --icon=dialog-error-symbolic "Command failed" @(cmd)
            canberra-gtk-play -i dialog-warning
