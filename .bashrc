#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# If running trom tty1 start xorg
if [ $(tty) == "/dev/tty1" ]; then
	source ~/.config/bash/graphical_session
	exit 0
else
	tput setaf 9
	echo "
 -=[  CaféHaine  ]=-
"
	pgrep obs&>/dev/null
	if [ $? -eq 0 ]; then
		echo "TU ES EN TRAIN DE STREAMER FAIS PAS LE CON
"
	fi
	tput sgr0
fi

# Used in sourced files to determine the max number of threads to use
__threads="$(nproc --ignore 1)"

# Environment

source ~/.config/bash/environment

# Prompt

source ~/.config/bash/prompt

# Aliases/wrappers

source ~/.config/bash/aliases

############################
# Machine specific configs #
############################

source ~/.imports
