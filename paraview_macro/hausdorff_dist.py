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


def generate_vn(s_in, s_name):
    sd = servermanager.Fetch(s_in)
    if not sd.IsA("vtkPolyData"):
        return s_in
    vn = sd.GetPointData().GetNormals()
    if vn is not None:
        return s_in
    sn = GenerateSurfaceNormals(Input=s_in)
    RenameSource("{}_vn".format(s_name), sn)
    return sn




def show_hausdorff_dist(s_list):
    s_num = len(s_list)
    if s_num == 2:
        print("Error! 2 source need to be selected")
        return
    # get names
    pxm = servermanager.ProxyManager();
    name0 = os.path.splitext(pxm.GetProxyName("sources", s_list[0]))[0]
    name1 = os.path.splitext(pxm.GetProxyName("sources", s_list[1]))[0]
    # generate vn if not exists
    s1 = generate_vn(s_list[0], name0)
    s2 = generate_vn(s_list[1], name1)
    sd1 = servermanager.Fetch(s1)
    sd2 = servermanager.Fetch(s2)
    p2c = sd1.IsA("vtkPolyData") and sd2.IsA("vtkPolyData")
    # create filter
    hd = HausdorffDistance(InputA=s1, InputB=s2)
    if not p2c:
        hd.TargetDistanceMethod = 'Point-to-Point'
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

s_list = active_obj.get_selected_sources()
show_hausdorff_dist(s_list)
