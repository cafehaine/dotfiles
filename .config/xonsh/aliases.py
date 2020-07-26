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
    vox new .venv
    vox activate .venv
    pip install --upgrade pip
    pip install -r requirements.txt

def _activate():
    """
    Search recursively for a vox .venv, and if found activate it.
    """

aliases['mkvenv'] = _mkvenv
aliases["deactivate"] = "vox deactivate"
aliases["activate"] = _activate

"""
activate() {
        local dir=$PWD
        while [ "$dir" != "/" ]; do
                if [ -f "$dir/.venv/bin/activate" ]; then
                        break
                fi
                dir=$(dirname $dir)
        done
        if [ -f "$dir/.venv/bin/activate" ]; then
                source "$dir/.venv/bin/activate"
        else
                "Could not find .venv"
        fi
}
"""
