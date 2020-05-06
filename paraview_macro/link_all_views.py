# -*- coding: utf-8 -*-
## @file link_all_views.py
## @brief set link for all view in active layout
## @author jiayanming

#### import the simple module from the paraview
from paraview.simple import *

#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

#get current view
cur_v = GetActiveView()
cur_l = GetLayout(cur_v)

#get view in same layout
#note this function return list only, for other informations,
# use ProxyManager.GetProxiesInGroup("views") (servermanager.py:2160)
v_list = GetViewsInLayout(cur_l)
itr = 1
for vi in v_list:
    if vi == cur_v: continue
    AddCameraLink(cur_v, vi, "link{}_{}".format(0, itr))
    itr = itr + 1
