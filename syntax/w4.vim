if exists("b:current_syntax")
    finish
endif
syn match W4Cmd '^%%.*$'
syn match W4Name '@[^@[:space:]]\+'
syn match W4Link '#\d\{10}'
syn match W4Op '-\{1,3}'
hi def link W4Cmd PreProc
hi def link W4Name String
hi def link W4Link Number
hi def link W4Op Operator
