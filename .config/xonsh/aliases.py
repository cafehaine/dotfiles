################
# Random utils #
################

aliases['ls']    = "ls --color=auto"
aliases['grep']  = "grep --color=auto"
aliases['diff']  = "diff --color=auto"
aliases['make']  = "make --jobs=$__threads"
aliases['ninja'] = "ninja -j $__threads"
aliases['lsblk'] = "lsblk -o NAME,SIZE,TYPE,MOUNTPOINT,LABEL,PARTLABEL"
aliases['df']    = "df -h"
aliases['free']  = "free -h"
aliases['du']    = "du -d1 -h"

#####################
# Virtual env (vox) #
#####################

def _mkvenv():
    """
    Create a virtual env, activate source it, and pip install requirements.txt.
    """
    from os.path import exists
    # Create a vox virtual environment and activate it
    vox new .venv
    vox activate .venv
    # Upgrade pip
    pip install --upgrade pip
    # Install requirememts if available
    if exists("requirements.txt"):
        pip install -r requirements.txt


def _activate():
    """
    Search in parent directories for a .venv, and if found activate it with vox.
    """
    from pathlib import Path
    curr_path = Path.cwd()
    #TODO this actually skips the root directory
    while curr_path.parent != curr_path:
        venv_path = curr_path.joinpath(".venv")
        if venv_path.is_dir():
            vox activate @(str(venv_path))
            return 0
        curr_path = curr_path.parent
    print("Could not find a .venv to activate.")
    return 1

aliases['mkvenv'] = _mkvenv
aliases["deactivate"] = "vox deactivate"
aliases["activate"] = _activate
