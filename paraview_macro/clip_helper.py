# -*- coding: utf-8 -*-
## @file clip_helper.py
## @brief clip with plane defined by (Rotation Center) and (Camera direction)
## @author jiayanming

import os.path
import math
from paraview.simple import *
from paraview.simple import _active_objects

#setup active object
active_obj = _active_objects()
cur_view = active_obj.get_view()
s_list = active_obj.get_selected_sources()

# get view direction vector
cam = cur_view.CameraPosition
old_f = cur_view.CameraFocalPoint
v_line = [old_f[i]-cam[i] for i in range(0, 3)]
len_v_line = 0
for i in range(0, 3):
    len_v_line += v_line[i] * v_line[i]
len_v_line = math.sqrt(len_v_line)
for i in range(0, 3):
    v_line[i] /= len_v_line

center = cur_view.CenterOfRotation

pxm = servermanager.ProxyManager()
for si in s_list:
    clip = Clip(Input=si)
    clip.ClipType = 'Plane'
    clip.Crinkleclip = 1
    clip.Scalars = [None, '']
    clip.ClipType.Origin = center
    clip.ClipType.Normal = v_line
    clipDisplay = Show(clip, cur_view)
    Hide(si, cur_view)
    Hide3DWidgets(proxy=clip.ClipType)
    name = os.path.splitext(pxm.GetProxyName("sources", si))[0]
    RenameSource("{}_clip".format(name), clip)
    cur_view.Update()
