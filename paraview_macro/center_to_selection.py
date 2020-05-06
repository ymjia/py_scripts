# -*- coding: utf-8 -*-
## @file center_to_selection.py
## @brief set Rotation Center to selected points
## @author jiayanming

#### import the simple module from the paraview
import math
from paraview.simple import *

def get_barycenter(data):
    avg_pt = [0, 0, 0]
    pt_num = data.GetNumberOfPoints() # total points
    if hasattr(data, 'GetPoint'): # unstructure data
        for idx in range(0, pt_num, 1):
            cur_pt = data.GetPoint(idx)
            for j in range(0, 3):
                avg_pt[j] += cur_pt[j]
        for j in range(0, 3):
            avg_pt[j] /= pt_num
        return avg_pt
    if hasattr(data, 'GetBlock'): # multiblock data
        for b in range (0, data.GetNumberOfBlocks()):
            b_data = data.GetBlock(b)
            if not b_data: continue
            for p in range (0, b_data.GetNumberOfPoints()):
                cur_pt = b_data.GetPoint(p)
                for j in range(0, 3):
                    avg_pt[j] += cur_pt[j]
        for j in range(0, 3):
            avg_pt[j] /= pt_num
        return avg_pt
    return None


def set_view_center(cur_view, center):
    cur_view.CenterOfRotation = center
    cam = cur_view.CameraPosition
    old_f = cur_view.CameraFocalPoint
    # get view direction vector
    v_line = [old_f[i]-cam[i] for i in range(0, 3)]
    len_v_line = 0
    for i in range(0, 3):
        len_v_line += v_line[i] * v_line[i]
    len_v_line = math.sqrt(len_v_line)
    for i in range(0, 3):
        v_line[i] /= len_v_line

    # new view direction
    new_line = [center[i] - cam[i] for i in range(0, 3)]

    # projection
    dot_p = 0
    for i in range(0, 3):
        dot_p += new_line[i] * v_line[i]
    new_v_line = [v_line[i] * dot_p for i in range(0, 3)]

    # set new focal point
    new_f = [cam[i] + new_v_line[i] for i in range(0, 3)]
    cur_view.CameraFocalPoint = new_f


# get active source.
cur_source = GetActiveSource()

# get active view
cur_view = GetActiveViewOrCreate('RenderView')

# get selection
cur_sel = cur_source.GetSelectionOutput(cur_source.Port)
sel_data = servermanager.Fetch(cur_sel)

# get barycenter
avg_pt = None
if sel_data.GetNumberOfPoints() > 0:
    avg_pt = get_barycenter(sel_data)

# set rotation center and focal point
if avg_pt:
    set_view_center(cur_view, avg_pt)
