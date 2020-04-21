# -*- coding: utf-8 -*-
## @file append_ext.py
## @brief append extension to all files with no extension in given dir
## @author jiayanming

from pyunpack import Archive
import os.path
import sys
from shutil import move
import pathlib

def append_ext(in_path, ext):
    for f in os.listdir(in_path):
        if not os.path.isfile(f):
            continue
        _, ext = os.path.splitext(f)
        if ext != "":
            continue
        f_full = os.path.join(in_path, f)
        move(f_full, f_full + ".tb")


in_path = str(sys.argv[1])
ext = ".tb"
if len(sys.argv) > 2:
    ext = str(sys.argv[2])
append_ext(in_path, ext)
