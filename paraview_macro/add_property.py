# -*- coding: utf-8 -*-
## @file add_property.py
## @brief add property to selected sources based on their name
## for file: path/xx.ply, try to find path/xx.txt as its custom property
## @author jiayanming

import os.path
from paraview.simple import *
from paraview.simple import _active_objects

#setup active object
active_obj = _active_objects()
cur_view = active_obj.get_view()
s_list = active_obj.get_selected_sources()
for si in s_list:
    # get names
    name = ""
    if hasattr(si, 'FileNames') and si.FileNames[0]:
        name = si.FileNames[0]
    if hasattr(si, 'FileName'):
        name = si.FileName

    if not name == "":
        name = os.path.splitext(name)[0] + ".txt"
        if not os.path.exists(name):
            name = ""

    # create filter
    ap = AddProperty(Input=si, FileName=name)
    ap_display = Show(ap, cur_view)
    ap_display.MapScalars = 1
    # display color
    if not name == "":
        ap_display.SetScalarBarVisibility(cur_view, True)
        customPropLUT = GetColorTransferFunction('CustomProp')
        customPropPWF = GetOpacityTransferFunction('CustomProp')

    Hide(si, cur_view)
    cur_view.Update()
