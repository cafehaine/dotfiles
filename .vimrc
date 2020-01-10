"==============
" Vundle stuff
"==============

set nocompatible
filetype off
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

Plugin 'VundleVim/Vundle.vim'
Plugin 'valloric/youcompleteme'
Plugin 'ap/vim-css-color'
Plugin 'yggdroot/indentline'

call vundle#end()
filetype plugin indent on

"======================
" YouCompleteMe config
"======================

set completeopt-=preview

"============
" indentLine
"============

let g:indentLine_char='│'
let g:indentLine_color_term='cyan'

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
filetype indent on
filetype plugin on

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

"Save with sudo when using W
command W w !sudo tee "%" > /dev/null

"=====================
" Custom key bindings
"=====================

" Tabs (kinda like firefox, but without Ctrl for tab switching)
nnoremap <unique> <C-T> :tabnew<CR>:Explore<CR>
nnoremap <unique> <C-W> :q<CR>
nnoremap <unique> <Tab> :tabnext<CR>
nnoremap <unique> <S-Tab> :tabprev<CR>

"========================
" Color and status stuff
"========================

highlight LineNr	ctermfg=grey	ctermbg=black
highlight Pmenu		ctermfg=grey	ctermbg=black
highlight PmenuSel	ctermfg=black	ctermbg=green

" Format the status line
hi User1 ctermbg=None	ctermfg=white
hi User2 ctermbg=None	ctermfg=darkgrey

" Statusline:
" [readonly][path] - [hovered char as hex] ---- [line/total lines] - [column]
set fillchars=stl:-
set statusline=%#Error#%r
set statusline+=%1*%F
set statusline+=%2*\ -\ %1*
set statusline+=char:%02B
set statusline+=%2*\ %=\ %1*
set statusline+=l:%3l\/%3L
set statusline+=%2*\ -\ %1*
set statusline+=c:%3v

