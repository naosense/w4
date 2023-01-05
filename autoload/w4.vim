if !has("python") && !has("python3")
    echoerr "Vim has to be compiled with +python or +python3 to run this"
    finish
endif

if !exists("g:w4_chrome_path") && !exists("g:w4_firefox_path")
    echoerr "Not set browser path"
    finish
endif

if !exists("g:w4_port")
    let g:w4_port = 8341
endif

fun! s:using_py3()
    if has('python3')
        return 1
    endif
        return 0
endfun

let s:using_python3 = s:using_py3()
let s:python_until_eof = s:using_python3 ? "python3 << EOF" : "python << EOF"
let s:python_cmd = s:using_python3 ? "py3 " : "py "
let s:python_command = s:using_python3 ? "python3" : "python"
let s:plugin_root_dir = fnamemodify(resolve(expand("<sfile>:p")), ":h")

exec s:python_until_eof
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, 'python'))
sys.path.insert(0, python_root_dir)
port = vim.eval('g:w4_port')
import main
EOF

let s:is_start = 0

fun! s:start()
    if has("win32")
        execute 'silent !start /b ' . s:python_command . ' ' . s:plugin_root_dir . '/python/server.py ' . g:w4_port
    else
        execute 'silent !(' . s:python_command . ' ' . s:plugin_root_dir . '/python/server.py ' . g:w4_port . ' && sleep 1) >/dev/null 2>&1 &'
    endif
    let s:is_start = 1
endfun


fun! s:open()
    if exists("g:w4_chrome_path")
        if has("win32")
            execute "silent !start " . g:w4_chrome_path . " --app=http://127.0.0.1:" . g:w4_port . "/index"
        else
            execute "silent !\"" . g:w4_chrome_path . "\" --app=http://127.0.0.1:" . g:w4_port . "/index"
        endif
    elseif exists("g:w4_firefox_path")
        if has("win32")
            execute "silent !start " . g:w4_firefox_path . " http://127.0.0.1:" . g:w4_port . "/index"
        else
            execute "silent !\"" . g:w4_firefox_path . "\" http://127.0.0.1:" . g:w4_port . "/index"
        endif
    endif
endfun

fun! s:autocmd()
    augroup w4
        autocmd!
        autocmd CursorMoved,CursorMovedi <buffer> call s:sync()
        autocmd BufWrite <buffer> call s:sync()
        autocmd VimLeave * call s:stop()
    augroup end
endfun

fun! s:sync()
exec s:python_until_eof
content = vim.eval('join(getline(1, line("$")), "\n")')
main.sync(content, port)
EOF
endfun

fun! s:stop()
exec s:python_until_eof
main.stop(port)
EOF
endfun

fun! s:name_idx()
    let lines = getline(1, '$')
    for line in lines
        if line =~ '^%%' && stridx(line, 'who') > 0
            let n = 1
            for col in split(line[2:], ' ')
                if col == 'who'
                    return n
                endif
                let n += 1
            endfor
        endif
    endfor
    echoerr "Can't find col names line, e.g. %% who what when where"
    finish
endfun

fun! s:split_char()
    let lines = getline(1, '$')
    for line in lines
        if line =~ '^%%' && stridx(line, 'col_split_char') > 0
            return split(line[2:], '=')[1]
        endif
        " 提前退出
        if line !~ '^%%'
            return ' '
        endif
    endfor
    return ' '
endfun

fun! s:trim(s)
    let len = len(a:s)
    let st = 0
    while st < len
        if a:s[st] == ' '
            let st += 1
        else
            break
        endif
    endwhile

    let ed = len - 1
    while ed > 0
        if a:s[ed] == ' '
            let ed -= 1
        else
            break
        endif
    endwhile
    return a:s[st:ed]
endfun

let s:col_split_char = s:split_char()

fun! s:collect_names()
    let names = []
    let lines = getline(1, '$')
    let name_idx = s:name_idx()
    for line in lines
        " skip cmd
        if line =~ '^%%'
            continue
        endif
        let cols = split(line, s:col_split_char)
        if len(cols) < 5
            continue
        endif
        for n in split(s:trim(cols[name_idx]), '@')
            call add(names, '@' . n)
        endfor
    endfor
    return names
endfun

fun! s:collect_events(pattern, limit)
    let events = []
    let lines = getline(1, '$')
    for line in lines
        " skip cmd
        if line =~ '^%%'
            continue
        endif
        let cols = split(line, s:col_split_char)
        if len(cols) < 5
            continue
        endif
        let first_4_col_str = join(cols[1:4], s:col_split_char)
        let word = s:trim(cols[0])
        let menu = s:trim(first_4_col_str)
        if word =~ a:pattern || menu =~ a:pattern
            let event = {'word': word, 'menu': menu}
            call add(events, event)
            if len(events) == a:limit
                return events
            endif
        endif
    endfor
    return events
endfun

fun! w4#suggestion(findstart, base)
    if a:findstart
        " 定位单词的开始处，注意补全也是从这个位置开始覆盖的
        let line = getline('.')
        let start = col('.') - 1
        while start > 0
            if line[start] == '@' || line[start] == '#'
                break
            endif
            if line[start] == s:col_split_char
                " 这里不加1会覆盖前面的空格
                let start += 1
                break
            endif
            let start -= 1
        endwhile
        return start
    else
        let res = []
        let head = a:base[0:0]
        if head == '@'
            let names = s:collect_names()
            for m in names
                if m =~ a:base
                    call add(res, m)
                endif
            endfor
            return res
        elseif head == '#'
            return s:collect_events('.*' . a:base[1:], 10)
        " 头部
        else
            return s:collect_events('.*' . a:base, 10)
        endif
    endif
endfun

fun! w4#browse()
    if !s:is_start
        call s:start()
        sleep 200m
        call s:sync()
    endif
    call s:open()
    call s:autocmd()
endfun