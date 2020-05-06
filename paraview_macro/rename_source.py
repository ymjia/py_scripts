# -*- coding: utf-8 -*-
## @file rename_view.py
## @brief rename source helper
## @author jiayanming
from paraview.simple import *
from paraview.simple import _active_objects

active_obj = _active_objects()
cur_source = active_obj.get_source()
target_name = input()
RenameSource(target_name, cur_source)
