# -*- coding: utf-8 -*-
## @file add_light.py
## @brief add a light to views in active layout
## @author jiayanming

from paraview.simple import *
from paraview.simple import _active_objects

active_obj = _active_objects()
cur_view = active_obj.get_view()

ly = GetLayout(cur_view)
v_list = GetViewsInLayout(ly) #view in cur layout

for vi in v_list:
    light = AddLight(view=vi)
    # Properties modified on light1
    light.Coords = 'Camera'
    light.Type = 'Directional'
    light.Position = [-1.0, 1.0, 1.0]
    light.FocalPoint = [1.0, -1.0, 0.0]
    # Properties modified on light
    light.Intensity = 0.5

Render()
