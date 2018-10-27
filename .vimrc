function PrefillTemplate()
	" exceptions based on the file extension
	let exceptions = {'h':'c_header', 'hpp':'cpp_header'}

	let templatename = get(exceptions,expand("%:e"),&filetype)
	let path = expand("~/.vimtemplates/".templatename)

	if filereadable(path)
		call append(0, readfile(path))
	else
		echo "PrefillTemplate: No template for ".templatename
	endif
endfunction

:autocmd BufNewFile * :call PrefillTemplate()
