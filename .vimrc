"==============
" Vundle stuff
"==============

set nocompatible
filetype off
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

Plugin 'VundleVim/Vundle.vim'          " package manager
Plugin 'valloric/youcompleteme'        " auto-completion
Plugin 'ap/vim-css-color'              " CSS color preview
Plugin 'yggdroot/indentline'           " space indented vertical indentation guide
Plugin 'tikhomirov/vim-glsl'           " GLSL syntax
Plugin 'loremipsum'                    " insert lorem ipsum paragraphs
Plugin 'alvan/vim-closetag'            " auto-close html/xml tags
Plugin 'datawraith/auto_mkdir'         " auto-create directories on :w
Plugin 'editorconfig/editorconfig-vim' " editorconfig is a standard to specify per-project configs
Plugin 'tibabit/vim-templates'         " load templates when opening an empty file
Plugin 'sirver/ultisnips'              " insert code snippets
Plugin 'unblevable/quick-scope'        " highlight chars to jump to using f or t

call vundle#end()
filetype plugin indent on

"======================
" YouCompleteMe config
"======================

set completeopt-=preview
let g:ycm_key_invoke_completion = ''

"============
" indentLine
"============

let g:indentLine_char='│'
let g:indentLine_color_term='cyan'
let g:indentLine_fileTypeExclude = ['json', 'markdown']

"=====================================
" netrw (vim default's file explorer)
"=====================================

" hide dotfiles by default (but not ../)
let g:netrwhide=1
let g:netrw_list_hide= '^\.\(\.\/\)\@!'

" hide the help banner
let g:netrw_banner=0

" case insensitive file sorting
let g:netrw_sort_options="i"

" multi-column layout
let g:netrw_liststyle=2

"===============
" vim-templates
"===============

let g:tmpl_search_paths = ['~/.vimtemplates']
let g:tmpl_author_name = 'CaféHaine'
let g:tmpl_company = 'CaféHaine'
let g:tmpl_author_email = 'kilian.guillaume@gmail.com'

"===========
" UltiSnips
"===========

"TODO find better bindings, and define binding for backward jump.
let g:UltiSnipsExpandTrigger="<c-b>"
let g:UltiSnipsJumpForwardTrigger="<c-b>"

"=============
" Quick-Scope
"=============

"Show highlights only when pressing 'jump' keys
let g:qs_highlight_on_keys = ['f', 'F', 't', 'T']

"================
" General config
"================

color cafehaine
syntax enable "Syntax coloring
set ai "Auto indent
set cursorline
set laststatus=2 "Always show status

set nu rnu "Relative + absolute line numbering
augroup numbertoggle
	autocmd!
	autocmd BufEnter,FocusGained,InsertLeave * set relativenumber
	autocmd BufLeave,FocusLost,InsertEnter   * set norelativenumber
augroup END

augroup spelltoggle
	autocmd!
	autocmd BufEnter,FocusGained,InsertLeave * set spell spelllang=en_us
	autocmd BufLeave,FocusLost,InsertEnter   * set nospell
augroup END

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

" Tabs (kinda like Firefox, but without Ctrl for tab switching)
nnoremap <unique> <C-T> :tabnew<CR>:Explore<CR>
nnoremap <unique> <C-W> :q<CR>
nnoremap <unique> <Tab> :tabnext<CR>
nnoremap <unique> <S-Tab> :tabprev<CR>

"============
" Statusline
"============

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
