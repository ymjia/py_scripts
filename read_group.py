# -*- coding: utf-8 -*-
## @file read_group.py
## @brief read clipboard file list as a group
## @author jiayanming
import os
import os.path
import math
from tkinter import Tk

from paraview.simple import *
# get clip board
r = Tk()
r.withdraw()
r.update()
file_str = str(r.selection_get(selection="CLIPBOARD"))
r.destroy()
file_list = file_str.split(";")

pxm = servermanager.ProxyManager()


def read_files(file_list):
    if len(file_list) < 1:
        return None
    file_name = os.path.split(file_list[0])[1]
    stem = os.path.splitext(os.fsdecode(file_name))[0]
    ext = os.path.splitext(os.fsdecode(file_name))[1]
    reader = OpenDataFile(file_list)
    if reader is None: return None
    RenameSource(stem, reader)
    return reader

def trim_last_number(name_str):
    c_num = len(name_str)
    idx = 1
    while idx < c_num:
        sub_tail = str(name_str[-1 * idx:])
        if not sub_tail.isdigit():
            break
        idx += 1
    if idx == c_num:
        return name_str
    return str(name_str[:-1 * idx + 1])


cur_source = read_files(file_list)
cur_view = GetActiveView()

if cur_source is not None and len(file_list) > 1:
    name = pxm.GetProxyName("sources", cur_source)
    gd = GroupTimeSteps(Input=cur_source)
    RenameSource("{}_list".format(trim_last_number(name)), gd)
    Hide(cur_source, cur_view)
    cur_source = gd
    
gd_display = Show(cur_source, cur_view)
ColorBy(gd_display, ['POINTS', 'tmp'])
ColorBy(gd_display, ['POINTS', ''])
cur_view.ResetCamera()
Render()
