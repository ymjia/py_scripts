# -*- coding: utf-8 -*-
## @file apply_all_visible.py
## @brief apply Representation property to all visible source in all visible view
## @author jiayanming

import os
import sys
dir_py_module = os.path.join(os.getcwd(), "..", "Sn3D_plugins", "scripts", "pv_module")
sys.path.append(dir_py_module)
from copy_display import pm_copy_display
from copy_display import get_view_source
from paraview.simple import *
from paraview.simple import _active_objects

active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()

ly = GetLayout(cur_view)
s_list = GetSources().values() #all sources list
v_list = GetViewsInLayout(ly) #view in cur layout

#use visible source as active source
base_source = get_view_source(s_list, cur_view)
cur_p =servermanager.GetRepresentation(base_source, cur_view)

#initial Color Array Name
init_ca = list(cur_p.ColorArrayName)
if init_ca[0] == None:
    ColorBy(cur_p, ['POINTS', 'tmp'])#trick direct use of ['POINT', ''] does not work
    ColorBy(cur_p, ['POINTS', ''])

#find all visible source
vs_list = [] #visible sources display properties
for vi in v_list:
    for si in s_list:
        n_port = si.SMProxy.GetNumberOfOutputPorts()
        for pi in range(0, n_port):
            dp = servermanager.GetRepresentation(si[pi], vi)
            if not dp or dp.Visibility == 0 : continue
            vs_list.append(dp)

#apply representation status
for pt_itr in vs_list:
    pm_copy_display(cur_p, pt_itr)
Render()
