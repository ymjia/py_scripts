# -*- coding: utf-8 -*-
## @file create_screenshots.py
## @brief create screenshots for mesh in given position
## @author jiayanming

import os.path
import math
from paraview.simple import *
from paraview.simple import _active_objects

# input data
list_case = ["case1", "case2"]
# versions to be compared
list_ver = ["input", "v1.1", "v1.2"]
# compare alg list
list_alg = ["rm_bd", "mereg"]
# screen shot view list

# use file.read() to get line strings from file
file_str = [
    "21.592487625427918, -3.9409709513281155, 14.064178593924428, 0, 31.229605061218003, -10.201408793119702, -84.26875223772231, 63.87174977105823, 30.0, -0.3711922959164563, 0.5909988812878556, 0.7161959241497909",
    "17.751875930449856, -1.708730201723125, 16.386248894128883, 0, 31.229605061218003, 65.8207005083766, 29.988416576619034, -65.03166947917572, 30.0, -0.071392276098892, -0.9145222379034997, -0.3981861616045869",
    "10.875073976381433, -2.5383559980146932, -10.683993265910901, 0, 31.229605061218003, -168.8604479975359, -36.20012032697253, -121.38788198253197, 30.0, -0.02947648613752865, -0.9420078679310953, 0.3342937533381327"]
list_view = [line.split(", ") for line in file_str]
list_number = [[float(str) for str in item] for item in list_view]
# list_view = [
#     [21.592487625427918, -3.9409709513281155, 14.064178593924428, 0, 31.229605061218003, -10.201408793119702, -84.26875223772231, 63.87174977105823, 30.0, -0.3711922959164563, 0.5909988812878556, 0.7161959241497909],
#     [17.751875930449856, -1.708730201723125, 16.386248894128883, 0, 31.229605061218003, 65.8207005083766, 29.988416576619034, -65.03166947917572, 30.0, -0.071392276098892, -0.9145222379034997, -0.3981861616045869],
#     [10.875073976381433, -2.5383559980146932, -10.683993265910901, 0, 31.229605061218003, -168.8604479975359, -36.20012032697253, -121.38788198253197, 30.0, -0.02947648613752865, -0.9420078679310953, 0.3342937533381327]]

def fill_var(in_list, idx, var):
    if isinstance(var, int) or isinstance(var, float):
        var = in_list[idx]
        return 1
    ac = len(var)
    var[:] = in_list[idx: idx + len(var)]
    return ac


class ScreenShotHelper:
    def __init__(self):
        paraview.simple._DisableFirstRenderCameraReset()

    def set_camera(self, v, camera_pos):
        idx = 0
        idx += fill_var(camera_pos, idx, v.CameraFocalPoint)
        idx += fill_var(camera_pos, idx, v.CameraParallelProjection)
        idx += fill_var(camera_pos, idx, v.CameraParallelScale)
        idx += fill_var(camera_pos, idx, v.CameraPosition)
        idx += fill_var(camera_pos, idx, v.CameraViewAngle)
        idx += fill_var(camera_pos, idx, v.CameraViewUp)

    def take_shot(self, view, cam, source, filename):
        HideAll(view)
        Show(source, view)
        self.set_camera(view, cam)
        view.Update()
        v_size = cur_v.ViewSize
        SaveScreenshot(filename, cur_v, ImageResolution=v_size, TransparentBackground=1)


#setup active object
active_obj = _active_objects()
cur_s = active_obj.get_source()
cur_v = active_obj.get_view()
s_list = active_obj.get_selected_sources()


pxm = servermanager.ProxyManager();
s_name = os.path.splitext(pxm.GetProxyName("sources", cur_s))[0]
ss = ScreenShotHelper()

# create a new 'SnDenoiseBilateral'
ss.take_shot(cur_v, list_number[0], cur_s, "c:/tmp/view0.png")
ss.take_shot(cur_v, list_number[1], cur_s, "c:/tmp/view1.png")
ss.take_shot(cur_v, list_number[2], cur_s, "c:/tmp/view2.png")
