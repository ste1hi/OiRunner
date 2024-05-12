# -*- coding: utf-8 -*-
import os
import shutil

FILEOUT = "#1:\nfile1\n#2:\nfile2\n#3:\nfile3\n"
GARBAGE = ["a.out", "a.exe", "~temp", "~err_temp", "~out"]
FREOPEN = 'freopen \n        ("in", "r"  , stdin),\n    freopen("out" , "w", stdout);'


def clean(filelist):
    for filename in filelist:
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)
