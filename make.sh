#!/bin/sh

# todo: run workflow without python3
# pyinstaller --additional-hooks-dir=workflow workflow/naver_spellcheck.py

cd workflow
zip -r ../papago.alfredworkflow .