# -*- coding: utf-8 -*-
import os

FILEOUT = "#1:\nfile1\n#2:\nfile2\n#3:\nfile3\n"
GARBAGE = ["a.out", "a.exe", "~temp", "~err_temp", "~out", ]
FREOPEN = 'freopen \n        ("in", "r"  , stdin),\n    freopen("out" , "w", stdout);'
HTML_WITHOUT_META_TAG = '<html><meta name="not_csrf" content></meta></html>'
HTML_WITHOUT_CONTENT = '<html><meta name="csrf-token"></meta></html>'
HTML_CORRECT = '<html><meta name="csrf-token" content="test_csrf_token"></meta></html>'


def clean(filelist):
    for filename in filelist:
        if os.path.exists(filename):
            os.remove(filename)
