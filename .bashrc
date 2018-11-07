#
# ~/.bashrc
#

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# If running trom tty1 start xorg
if [ $(tty) == "/dev/tty1" ]; then
	startx
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

centertext()
{
	local padding=$(( $1 - ${#2} ))
	local before=$(( $padding / 2 ))
	local after=$(( $padding - $before ))
	if [ $before -gt 0 ]; then
		printf ' %.0s' $(seq 1 $before)
	fi
	echo -n $2
	if [ $after -gt 0 ]; then
		printf ' %.0s' $(seq 1 $after)
	fi
	echo ''
}

currdir()
{
	local pwd
	if [ "$PWD" == "/" ]; then
		pwd="/"
	elif [ "$PWD" == $HOME ]; then
		pwd="~"
	else
		pwd=${PWD##*/}
	fi
	local len=${#pwd}
	if [ $len -gt 11 ]; then
		pwd=${pwd:0:10}.
	elif  [ $len -lt 11 ]; then
		pwd=$(centertext 11 "$pwd")
	fi
	echo $pwd
}

errcolor()
{
	LASTERR=$?
	if [ $LASTERR -eq 0 ]; then
		tput setaf 2
	else
		tput setaf 1
	fi
	exit $LASTERR
}

reset="$(tput sgr0)"

PS1='\$[\[$(errcolor)\]$(centertext 3 $?)\[${reset}\]] \A $(currdir)> '

source .imports
