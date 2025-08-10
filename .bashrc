# If not running interactively, don't do anything
[[ $- != *i* ]] && return

shopt -s extglob
shopt -s globstar

# Aliases
alias hx=helix
alias ls="ls --color=auto"
alias mkvenv="python -m venv .venv"
alias a="source .venv/bin/activate"

# Bash stuff
source /usr/share/doc/pkgfile/command-not-found.bash
export HISTCONTROL=erasedups
export HISTSIZE=10000
shopt -s autocd
shopt -s extglob

[[ -r "/usr/share/z/z.sh" ]] && source /usr/share/z/z.sh
