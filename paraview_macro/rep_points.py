# -*- coding: utf-8 -*-
## @file rep_points.py
## @brief set representation to Point Gaussian for current source
## @author jiayanming
import os
import sys
dir_py_module = os.path.join(os.getcwd(), "..", "Sn3D_plugins", "scripts", "pv_module")
sys.path.append(dir_py_module)

from paraview.simple import *
from copy_display import get_view_source

s_list = GetSources().values() #all sources list
cur_view = GetActiveView()
cur_source = get_view_source(s_list, cur_view)
cur_p = GetDisplayProperties(cur_source, cur_view)
cur_p.Representation = 'Point Gaussian'
cur_p.GaussianRadius = 0
