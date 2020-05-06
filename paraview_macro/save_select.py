# -*- coding: utf-8 -*-
## @file save_select.py
## @brief save selected sources to ply file
## @author jiayanming

import os.path
from paraview.simple import *
from paraview.simple import _active_objects

#setup active object
active_obj = _active_objects()
s_list = active_obj.get_selected_sources()
pxm = servermanager.ProxyManager();
output_dir = input()
valid_path = True
try:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
except:
    valid_path = False
if valid_path:
    for si in s_list:
        s_name = os.path.splitext(pxm.GetProxyName("sources", si))[0]
        o_name = os.path.join(output_dir, s_name + ".ply")
        SaveData(o_name, proxy=si, ColorArrayName=['POINTS', ''], LookupTable=None)
else:
    print("input dir invalid")
