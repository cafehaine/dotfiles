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

:autocmd BufNewFile * :call PrefillTemplate()

highlight ExtraWhitespace ctermbg=red guibg=red
:autocmd Syntax * syn match ExtraWhitespace /\s\+$\| \+\ze\t/