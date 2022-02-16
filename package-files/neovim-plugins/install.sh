#!/bin/bash

nvim -c 'PlugInstall|q|q'
nvim -c 'CocInstall -sync coc-snippets coc-marketplace coc-explorer coc-eslint coc-html coc-java coc-go coc-flutter coc-python coc-rls coc-sh coc-clangd coc-texlab coc-emmet coc-vimlsp coc-css coc-yaml coc-json|q|q'
