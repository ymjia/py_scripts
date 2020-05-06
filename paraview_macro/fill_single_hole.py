# -*- coding: utf-8 -*-
## @file fill_single_hole.py
## @brief fill the nearest hole of selected point
## @author jiayanming

#### import the simple module from the paraview
import os.path
from paraview.simple import *
from paraview.simple import _active_objects


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


#setup active object
active_obj = _active_objects()
cur_view = active_obj.get_view()
cur_source = active_obj.get_source()

# get selection
cur_sel = cur_source.GetSelectionOutput(cur_source.Port)
sel_data = servermanager.Fetch(cur_sel)

# get barycenter
avg_pt = None
if sel_data.GetNumberOfPoints() > 0:
    avg_pt = get_barycenter(sel_data)

# create a new 'SnFillHole'
fill = SnFillHole(Input=cur_source)

# Properties modified on snFillHole1
fill.FillType = 'PickHole'
if not avg_pt is None:
    fill.center = avg_pt
fill.MaxV = 0
# show data in view
Show(fill, cur_view)
Hide3DWidgets(proxy=fill)
Hide(cur_source, cur_view)
cur_view.Update()
