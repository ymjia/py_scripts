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


# view positions in layout

# split layout and store positions
def split_layout(l, s_num):
    if s_num == 2:
        pos = l.SplitHorizontal(0, 0.5)
        return [pos, pos + 1]

    # 3 view horizontally
    if s_num == 3:
        pos = l.SplitHorizontal(0, 0.33)
        pos2 = l.SplitHorizontal(pos + 1, 0.5)
        return [pos, pos2, pos2 + 1]

    # 2 X 2
    if s_num == 4:
        tmp = l.SplitHorizontal(0, 0.5)
        pos0 = l.SplitVertical(tmp, 0.5)
        pos1 = l.SplitVertical(tmp + 1, 0.5)
        return [pos0, pos0 + 1, pos1, pos1 + 1]

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
        return l_pos

# assign new views, show selected sources and link views
#renderView1.InteractionMode = '2D'

#setup active object
active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()

# change representation type
s_list = active_obj.get_selected_sources()
s_num = len(s_list)
# is all picture
all_pic = True
for s in s_list:
    sd = servermanager.Fetch(s)
    if not sd.IsA("vtkImageData"):
        all_pic = False
        break

    
pxm = servermanager.ProxyManager()
if all_pic and s_num < 4:
    l = CreateLayout('Pic_{}'.format(s_num))
    l_pos = split_layout(l, s_num * 2)
    for si, s in enumerate(s_list):
        name = os.path.splitext(pxm.GetProxyName("sources", s))[0]
        v = CreateRenderView(False, registrationName = name)
        v.InteractionMode = '2D'
        v.CameraParallelProjection = 1
        Show(s, v)
        sv = CreateView('SpreadSheetView', registrationName = "{}_d".format(name))
        #sv.SelectionOnly = 1
        Show(s, sv)
        l.AssignView(l_pos[si * 2], v)
        l.AssignView(l_pos[si * 2 + 1], sv)
    # link cameras
    v0 = l.GetView(l_pos[0])
    for i in range(1, s_num):
        time_str = time.mktime(datetime.now().timetuple())
        cur_v = l.GetView(l_pos[i * 2])
        AddCameraLink(v0, cur_v, "l{}{}{}".format(time_str, 0, i))
    v0.ResetCamera()
    SetActiveView(v0)
        
elif s_num < 7:
    name0 = ""
    l = CreateLayout('Compare_{}'.format(s_num))
    l_pos = split_layout(l, s_num)
    v0 = None
    for i, s in enumerate(s_list):
        name = os.path.splitext(pxm.GetProxyName("sources", s))[0]
        v = CreateRenderView(False, registrationName=name)
        l.AssignView(l_pos[i], v)
        Show(s, v)
    v0 = l.GetView(l_pos[0])#link all with first view
    for i in range(0, s_num):
        v = l.GetView(l_pos[i])
        time_str = time.mktime(datetime.now().timetuple())
        AddCameraLink(v0, v, "l{}{}{}".format(time_str, 0, i))
    # render results
    v0.ResetCamera()
    SetActiveView(v0)
    Render()
