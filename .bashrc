# If not running interactively, don't do anything
[[ $- != *i* ]] && return

shopt -s extglob
shopt -s globstar

export PATH=$PATH:~/.local/bin

export EDITOR=hx

# Aliases
if ! which hx 2> /dev/null; then
  alias hx=helix
  export EDITOR=helix
fi
alias ls="ls --color=auto"
alias mkvenv="python -m venv .venv"
alias a="source .venv/bin/activate"

# Bash stuff
[[ -r "/usr/share/doc/pkgfile/command-not-found.bash" ]] && source /usr/share/doc/pkgfile/command-not-found.bash
export HISTCONTROL=erasedups
export HISTSIZE=10000
shopt -s autocd
shopt -s extglob

[[ -r "/usr/share/z/z.sh" ]] && source /usr/share/z/z.sh
eval "$(starship init bash)"
