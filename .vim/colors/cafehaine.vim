" My custom terminal only color scheme for vim, based on delek

runtime colors/delek.vim

let g:colors_name = "cafehaine"

" File explorer
hi Directory cterm=NONE ctermfg=Blue

" Tab bar
hi TabLine     cterm=NONE ctermfg=White ctermbg=NONE
hi TabLineFill cterm=NONE ctermfg=White ctermbg=NONE
hi TabLineSel  cterm=NONE ctermfg=White ctermbg=Black

" syntax highlighting
hi Comment        cterm=NONE ctermfg=DarkGreen
hi SpecialComment cterm=NONE ctermfg=Green

hi Constant cterm=NONE ctermfg=Yellow
hi Boolean  cterm=NONE ctermfg=LightBlue
hi Number   cterm=NONE ctermfg=LightGreen

hi Identifier cterm=NONE ctermfg=Cyan
hi PreProc    cterm=NONE ctermfg=Magenta
hi Special    cterm=NONE ctermfg=LightRed

hi Statement cterm=bold ctermfg=Blue
hi Operator  cterm=NONE ctermfg=LightBlue
hi Type      cterm=NONE ctermfg=Blue

" 80 col
hi ColorColumn ctermbg=black

" Line numbers
hi LineNr                  ctermfg=grey  ctermbg=black
hi CursorLineNr cterm=NONE ctermfg=white ctermbg=darkgray
hi CursorLine   cterm=NONE

" Popups
hi Pmenu      ctermfg=Gray  ctermbg=Black
hi PmenuSel   ctermfg=Black ctermbg=DarkGreen
hi PmenuSbar                ctermbg=Black
hi PmenuThumb               ctermbg=DarkGray

" Format the status line
hi User1 ctermbg=NONE ctermfg=white
hi User2 ctermbg=NONE ctermfg=darkgrey
