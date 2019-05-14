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

cur_view = GetActiveView()

if (len(file_list) > 2):
    first_file = file_list[0]
    ext = os.path.splitext(os.fsdecode(first_file))[1]
    print(os.path.splitext(os.fsdecode(first_file))[0])
    print(ext)
    reader_list = None
    if ext == ".rge":
        reader_list = RGEreader(FileNames=file_list)
    if ext == ".asc":
        reader_list = ASCreader(FileNames=file_list)
    if ext == ".ply":
        reader_list = PLYReader(FileNames=file_list)
    if ext == ".ac":
        reader_list = ACreader(FileNames=file_list)
    if reader_list is not None:
        name = pxm.GetProxyName("sources", reader_list)[:-1]
        gd = GroupTimeSteps(Input=reader_list)
        RenameSource("{}_list".format(name), gd)
        gd_display = Show(gd, cur_view)
        Hide(reader_list, cur_view)
        ColorBy(gd_display, ['POINTS', 'tmp'])
        ColorBy(gd_display, ['POINTS', ''])
        cur_view.ResetCamera()
        Render()
