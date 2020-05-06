# -*- coding: utf-8 -*-
## @file rename_view.py
## @brief rename view to first visible source in it
## @author jiayanming

import os
import sys
from paraview.simple import *
from paraview.simple import _active_objects

active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()

ly = GetLayout(cur_view)
s_list = GetSources().values() #all sources list
v_list = GetViewsInLayout(ly) #view in cur layout

#find all visible source
vs_list = [] #visible sources display properties
pxm = servermanager.ProxyManager();
for vi in v_list:
    for si in s_list:
        dp = servermanager.GetRepresentation(si, vi)
        if not dp or dp.Visibility == 0 : continue
        name = os.path.splitext(pxm.GetProxyName("sources", si))[0]
        RenameView(name, vi)
        break
