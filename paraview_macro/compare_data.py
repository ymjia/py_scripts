# -*- coding: utf-8 -*-
## @file compare_data.py
## @brief set compare views for selected sources, most support number: 6
## @author jiayanming

#### import the simple module from the paravie
import os.path
from paraview.simple import *
from paraview.simple import _active_objects
from datetime import datetime
import time
#setup active object
active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()

# change representation type
s_list = active_obj.get_selected_sources()
s_num = len(s_list)

l = CreateLayout('Compare_{}'.format(s_num))

# view positions in layout
l_pos = []

# split layout and store positions
if s_num == 2:
    pos = l.SplitHorizontal(0, 0.5)
    l_pos = [pos, pos + 1]

# 3 view horizontally
if s_num == 3:
    pos = l.SplitHorizontal(0, 0.33)
    pos2 = l.SplitHorizontal(pos + 1, 0.5)
    l_pos = [pos, pos2, pos2 + 1]

# 2 X 2
if s_num == 4:
    tmp = l.SplitHorizontal(0, 0.5)
    pos0 = l.SplitVertical(tmp, 0.5)
    pos1 = l.SplitVertical(tmp + 1, 0.5)
    l_pos = [pos0, pos0 + 1, pos1, pos1 + 1]

# 2 X 2 + 1 / 3 X 2
if s_num == 5 or s_num == 6:
    # split horizontally to 3
    tmp1 = l.SplitHorizontal(0, 0.33)
    tmp2 = l.SplitHorizontal(tmp1 + 1, 0.5)
    tmp3 = tmp2 + 1
    pos0 = l.SplitVertical(tmp1, 0.5)
    pos1 = l.SplitVertical(tmp2, 0.5)
    pos2 = tmp3
    if s_num == 6:
        # split last one
        pos2 = l.SplitVertical(tmp3, 0.5)
    l_pos = [pos0, pos0 + 1, pos1, pos1 + 1, pos2]
    if s_num == 6:
        l_pos.append(pos2 + 1)

# assign new views, show selected sources and link views
if s_num < 7:
    pxm = servermanager.ProxyManager()
    name0 = ""
    v0 = None
    for i in range (0, s_num):
        name = os.path.splitext(pxm.GetProxyName("sources", s_list[i]))[0]
        v = CreateRenderView(False, registrationName=name)
        l.AssignView(l_pos[i], v)
        Show(s_list[i], v)
        if i == 0:
            v0 = v
            name0 = name
        else: #link all with first view
            time_str = time.mktime(datetime.now().timetuple())
            AddCameraLink(v0, v, "l{}{}{}".format(time_str, 0, i))
    # render results
    v0.ResetCamera()
    SetActiveView(v0)
    Render()
