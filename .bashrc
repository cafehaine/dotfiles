#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Used in sourced files to determine the max number of threads to use
__threads="$(nproc --ignore 2)"

# Environment
source ~/.config/bash/environment

# If running trom tty1 and WAYLAND_DISPLAY isn't set, start GUI
if [ $(tty) == "/dev/tty1" -a -z "$SESSION_STARTED" ]; then
	source ~/.config/bash/graphical_session
	exit 0
else
	tput setaf 9
	echo "
 -=[  $USER @ $HOSTNAME  ]=-
"
	pgrep obs&>/dev/null
	if [ $? -eq 0 ]; then
		echo "TU ES EN TRAIN DE STREAMER FAIS PAS LE CON
"
	fi
	tput sgr0
fi

# Prompt

source ~/.config/bash/prompt

# Aliases/wrappers

source ~/.config/bash/aliases

############################
# Machine specific configs #
############################

source ~/.imports
