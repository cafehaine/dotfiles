"================
" File templates
"================

function PrefillTemplate()
	" exceptions based on the file extension
	let exceptions = {'h':'c_header', 'hpp':'cpp_header', 'inc.php':'php_class'}

	let templatename = get(exceptions,expand("%:e:e"),&filetype)
	let path = expand("~/.vimtemplates/".templatename)

	if filereadable(path)
		call append(0, readfile(path))
	else
		echo "PrefillTemplate: No template for ".templatename
	endif
endfunction

filetype on

autocmd BufNewFile * call PrefillTemplate()

"================
" General config
"================

syntax enable "Syntax coloring
set ai "Auto indent
set nu "Line numbering
set laststatus=2 "Always show status

"Override non breaking space, tabulation and trailing whitespace display
set listchars=nbsp:␣,tab:\│\ ,trail:─
set list

set nocompatible
set backspace=indent,eol,start

" Set the tab size to 8
set tabstop=8
set shiftwidth=8
set noexpandtab

" Highlight column 81
highlight ColorColumn ctermbg=black
set colorcolumn=81

set title titlestring=%F%r%w%h\ -\ vim "Change title

set path+=** "Make find recursive

set wildmenu "Pretty menu on tab completion

set mouse=a "Enable mouse selection

"========================
" Color and status stuff
"========================

highlight LineNr	ctermfg=grey ctermbg=black
" Format the status line
hi User1 ctermbg=None	ctermfg=white
hi User2 ctermbg=None	ctermfg=darkgrey

" Statusline:
" [path] - [hovered char as hex] ---- [line/total lines] - [column]
set fillchars=stl:-
set statusline=%2*%1*%F%r%w%h%2*\ -\ %1*char:%02B%2*\ %=\ %1*l:%3l\/%3L%2*\ -\ %1*c:%3c%2*

