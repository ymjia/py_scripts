# -*- coding: utf-8 -*-
## @file apply_all_select.py
## @brief apply Representation property to all selected source in active view
## @author jiayanming

# import custom modules ####
import os
import sys
dir_py_module = os.path.join(os.getcwd(), "..", "Sn3D_plugins", "scripts", "pv_module")
sys.path.append(dir_py_module)
from copy_display import pm_copy_display

#### import the simple module from the paraview
from paraview.simple import *
from paraview.simple import _active_objects
#### disable automatic camera reset on 'Show'
#setup active object
active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()

# get display properties
cur_p = GetDisplayProperties(cur_source, cur_view)

#initialize ColorArrayName if necessary
init_ca = list(cur_p.ColorArrayName)
if init_ca[0] == None:
    ColorBy(cur_p, ['POINTS', 'tmp'])#trick direct to ['POINTS', ''] does not work
    ColorBy(cur_p, ['POINTS', ''])

# change representation type
s_list = active_obj.get_selected_sources()
for s_itr in s_list:
    if s_itr == cur_source: continue
    pt_itr = GetDisplayProperties(s_itr, cur_view)
    pm_copy_display(cur_p, pt_itr)
#Render(cur_view)

