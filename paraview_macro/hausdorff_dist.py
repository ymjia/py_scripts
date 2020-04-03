# -*- coding: utf-8 -*-
## @file hausdorff_dist.py
## @brief set compare views hausdorffDistance between two mesh
## @author jiayanming

#### import the simple module from the paraview
import os.path
from paraview.simple import *
from paraview.simple import _active_objects
from datetime import datetime
import time
#setup active object
active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()


def set_hd_output_display(display, view):
    ColorBy(display, ('POINTS', 'Distance'))
    display.SetScalarBarVisibility(view, True)
    display.MapScalars = 1


s_list = active_obj.get_selected_sources()
s_num = len(s_list)

if s_num == 2:
    # get names
    pxm = servermanager.ProxyManager();
    name0 = os.path.splitext(pxm.GetProxyName("sources", s_list[0]))[0]
    name1 = os.path.splitext(pxm.GetProxyName("sources", s_list[1]))[0]
    # create filter
    hd = HausdorffDistance(InputA=s_list[0], InputB=s_list[1])
    SetActiveSource(hd)    # set active source to hd to find transfer function
    RenameSource("{}_{}".format(name0, name1), hd)
    
    ly = CreateLayout('Hdf_{}{}'.format(name0, name1))
    v0 = CreateRenderView(False, registrationName=name0)
    v1 = CreateRenderView(False, registrationName=name1)
    out0 = OutputPort(hd, 0)
    out1 = OutputPort(hd, 1)
    display0 = Show(out0, v0)
    display1 = Show(out1, v1)
    set_hd_output_display(display0, v0)
    set_hd_output_display(display1, v1)

    # Rescale transfer function
    distanceLUT = GetColorTransferFunction('Distance')
    distancePWF = GetOpacityTransferFunction('Distance')
    distanceLUT.ApplyPreset('hausdorff', True)
    distancePWF.ApplyPreset('hausdorff', True)
    distanceLUT.RescaleTransferFunction(0.0, 0.1)
    distancePWF.RescaleTransferFunction(0.0, 0.1)

    AddCameraLink(v0, v1, "h_{}".format(time.mktime(datetime.now().timetuple())))
    v0.ResetCamera()
    SetActiveView(v0)
    Render()    
