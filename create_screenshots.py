# -*- coding: utf-8 -*-
## @file create_screenshots.py
## @brief create screenshots for mesh in given position
## @author jiayanming
import os
import os.path
import math
from paraview.simple import *
from paraview.simple import _active_objects

def get_sub_dir(cur):
    return [name for name in os.listdir(cur)
            if os.path.isdir(os.path.join(cur, name))]

dir_input = ""
dir_output = "c:/output/"
# versions to be compared
list_ver = ["input", "v11", "v12"]
# input data
list_case = ["case1", "case2"]
# compare alg list
list_alg = ["rm_bd", "merge"]
# screen shot view list

# read view list from input config file
# use file.read() to get line strings from file
file_str = [
    "21.592487625427918, -3.9409709513281155, 14.064178593924428, 0, 31.229605061218003, -10.201408793119702, -84.26875223772231, 63.87174977105823, 30.0, -0.3711922959164563, 0.5909988812878556, 0.7161959241497909",
    "17.751875930449856, -1.708730201723125, 16.386248894128883, 0, 31.229605061218003, 65.8207005083766, 29.988416576619034, -65.03166947917572, 30.0, -0.071392276098892, -0.9145222379034997, -0.3981861616045869",
    "10.875073976381433, -2.5383559980146932, -10.683993265910901, 0, 31.229605061218003, -168.8604479975359, -36.20012032697253, -121.38788198253197, 30.0, -0.02947648613752865, -0.9420078679310953, 0.3342937533381327"]

list_view = [line.split(", ") for line in file_str]
list_number = [[float(str) for str in item] for item in list_view]

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

def read_files(file_list):
    if len(file_list) < 1:
        return None
    file_name = os.path.split(file_list[0])[1]
    stem = os.path.splitext(os.fsdecode(file_name))[0]
    ext = os.path.splitext(os.fsdecode(file_name))[1]
    reader = OpenDataFile(file_list)
    if reader is None: return None
    RenameSource(stem, reader)
    return reader

def trim_last_number(name_str):
    c_num = len(name_str)
    idx = 1
    while idx < c_num:
        sub_tail = str(name_str[-1 * idx:])
        if not sub_tail.isdigit():
            break
        idx += 1
    if idx == c_num:
        return name_str
    return str(name_str[:-1 * idx + 1])

# read file or file list and render in given view
def read_and_render(file_list, cur_view):
    reader = read_files(file_list)
    if reader is None:
        return None
    if len(file_list) > 1:
        name = pxm.GetProxyName("sources", reader)
        gd = GroupTimeSteps(Input=cur_source)
        RenameSource("{}_list".format(trim_last_number(name)), gd)
        HideAll(cur_view)
        reader = gd
    gd_display = Show(reader, cur_view)
    ColorBy(gd_display, ['POINTS', 'tmp'])
    ColorBy(gd_display, ['POINTS', ''])
    cur_view.ResetCamera()
    Render()
    return reader

    
def create_shot(file_list, cam_list, out_dir):
    cur_view = CreateRenderView()
    cur_source = read_and_render(file_list, cur_view)
    ScreenShotHelper ss
    for i in range(0, len(cam_list)):
        ss.take_shot(cur_view, cam_list[i], cur_source,
                     "{}_v{}.png".format(out_dir, i))_
    

def read_cam(case_name):
    case_file = os.path.join(dir_input, case_name, "config.txt")
    content = None
    with open(case_file) as f:
        content = f.readlines()
    return [l.strip() for l in content]

#setup active object
# get all concerned file names
# case/version/alg
file_dir = [[ci, vi, [os.path.join(dir_output, ci, vi)
                      for vi in list_ver]] for ci in list_case]


#create shot
for case in file_dir:
    case_name = case[0]
    ver_name = case[1]
    case_files = case[2]
    cam_list = read_cam(case_name)
    for alg in list_alg:
        file_alg = os.path.join(file_dir, alg)
        file_list = file_alg
        if os.path.isdir(file_alg):
            file_list = os.path.listdir(file_alg)
        create_shot(file_list, read_cam(case_name), os.path.join(dir_output, case_name, ver_name, "ss")

print(file_dir)


# read data

# pxm = servermanager.ProxyManager();
# s_name = os.path.splitext(pxm.GetProxyName("sources", cur_s))[0]
# ss = ScreenShotHelper()

# create a new 'SnDenoiseBilateral'
#ss.take_shot(cur_v, list_number[0], cur_s, "c:/tmp/view0.png")
#ss.take_shot(cur_v, list_number[1], cur_s, "c:/tmp/view1.png")
#ss.take_shot(cur_v, list_number[2], cur_s, "c:/tmp/view2.png")
