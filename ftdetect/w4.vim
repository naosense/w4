autocmd BufNewFile,BufRead *.w4
    \ set filetype=w4 |
    \ set completeopt=menu,menuone,noinsert |
    \ set completefunc=w4#suggestion

augroup w4
    autocmd!
    " 如果菜单可见enter选择当前选项，否则回车
    " 下面三行配置是为了让在换行时自动加上时间戳作为每一行的唯一标识
    autocmd filetype w4 inoremap <expr> <CR> pumvisible() ? "\<C-Y>" : "\<CR>\<C-R>='#' . strftime('%m%d%H%M%S')<CR> "
    autocmd filetype w4 nnoremap o o<C-R>='#' . strftime('%m%d%H%M%S')<CR><SPACE>
    autocmd filetype w4 nnoremap O O<C-R>='#' . strftime('%m%d%H%M%S')<CR><SPACE>

    autocmd filetype w4 inoremap <expr> @ pumvisible() ? "@" : "@\<C-X>\<C-U>"
    autocmd filetype w4 inoremap <expr> # pumvisible() ? "#" : "#\<C-X>\<C-U>"
    autocmd filetype w4 inoremap <expr> <TAB> pumvisible() ? "\<TAB>" : "\<C-X>\<C-U>"
augroup end