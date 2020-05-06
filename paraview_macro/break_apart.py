# -*- coding: utf-8 -*-
## @file break_apart.py
## @brief break sequenced input to seperate sources
## @author jiayanming

import os.path
from paraview.simple import *
from paraview.simple import _active_objects

active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()

f_list = cur_source.FileNames
if f_list:
    Delete(cur_source)
    del cur_source
    for f in f_list:
        stem = os.path.basename(f)
        tmp_source = OpenDataFile(f)
        if not tmp_source: continue
        RenameSource(stem, tmp_source)
        Show(tmp_source, cur_view)
    cur_view.ResetCamera()
