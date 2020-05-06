# -*- coding: utf-8 -*-
## @file copy_display.py
## @brief useful functions
## @author jiayanming

from paraview.simple import *

## @brief copy display property from org_dp to dst_dp
## @param servermanager.GeometryRepresentation
def pm_copy_display(org_dp, dst_dp):
    if not(org_dp) or not(dst_dp): return
    #representation
    dst_dp.Representation = org_dp.Representation
    dst_dp.BackfaceRepresentation = org_dp.BackfaceRepresentation
    #colors
    ColorBy(dst_dp, list(org_dp.ColorArrayName))#color array
    dst_dp.AmbientColor = org_dp.AmbientColor
    dst_dp.DiffuseColor = org_dp.DiffuseColor
    dst_dp.EdgeColor = org_dp.EdgeColor

    dst_dp.BackfaceAmbientColor = org_dp.BackfaceAmbientColor
    dst_dp.BackfaceDiffuseColor = org_dp.BackfaceDiffuseColor
    #color map
    dst_dp.MapScalars = org_dp.MapScalars
    #Opacity
    dst_dp.Opacity = org_dp.Opacity
    dst_dp.BackfaceOpacity = org_dp.BackfaceOpacity
    #lightning
    dst_dp.Interpolation = org_dp.Interpolation
    dst_dp.Specular = org_dp.Specular
    #display size
    dst_dp.PointSize = org_dp.PointSize
    dst_dp.LineWidth = org_dp.LineWidth
    dst_dp.GaussianRadius = org_dp.GaussianRadius

# return selected source if it is visible
# or first visible source in current view
def get_view_source(s_list, cur_view):
    cur_source = GetActiveSource()
    if cur_source:
        n_port = cur_source.SMProxy.GetNumberOfOutputPorts()
        dp = servermanager.GetRepresentation(cur_source, cur_view)
        if dp and dp.Visibility == 1:
            return cur_source
    for si in s_list:
        n_port = si.SMProxy.GetNumberOfOutputPorts()
        for pi in range(0, n_port):
            dp = servermanager.GetRepresentation(si[pi], cur_view)
            if dp and dp.Visibility == 1:
                return si[pi]
