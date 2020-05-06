# -*- coding: utf-8 -*-
## @file group_together.py
## @brief read all sequence files in one multiblock
## @author jiayanming

import os.path
from paraview.simple import *
from paraview.simple import _active_objects

active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()
pxm = servermanager.ProxyManager()
name = pxm.GetProxyName("sources", cur_source)[:-1]

gd = GroupTimeSteps(Input=cur_source)
RenameSource("{}_list".format(name), gd)
gd_display = Show(gd, cur_view)
Hide(cur_source, cur_view)

ColorBy(gd_display, ['POINTS', 'tmp'])
ColorBy(gd_display, ['POINTS', ''])
cur_view.ResetCamera()
Render()
