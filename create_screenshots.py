# -*- coding: utf-8 -*-
## @file create_screenshots.py
## @brief create screenshots for mesh in given position
## @author jiayanming
import os
import os.path
import math
from paraview.simple import *
from paraview.simple import _active_objects

pxm = servermanager.ProxyManager()

# directory operations
def get_sub_dir(cur):
    return [name for name in os.listdir(cur)
            if os.path.isdir(os.path.join(cur, name))]


def get_file(folder, stem):
    if not os.path.exists(folder):
        return None
    for f in os.listdir(folder):
        cur_stem = os.path.splitext(f)[0]
        if cur_stem == stem:
            return os.path.join(folder, f)
    return None

# get all file from folder except subdir
def get_file_list(folder):
    return [name for name in os.listdir(folder)
            if not os.path.isdir(os.path.join(folder, name))]


dir_input = "c:/data/test_framwork/input/"
dir_output = "c:/data/test_framwork/output/"
# versions to be compared
list_ver = ["v11", "v12"]
# input data
list_case = ["case1", "case2"]
# compare alg list
list_alg = ["smooth", "merge"]

# fill camera variable from number list
def fill_var(in_list, idx, var):
    if isinstance(var, int) or isinstance(var, float):
        var = in_list[idx]
        return 1
    ac = len(var)
    var[:] = in_list[idx: idx + len(var)]
    return ac

# class for screenshots
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
        v_size = view.ViewSize
        SaveScreenshot(filename, view, ImageResolution=v_size, TransparentBackground=1)


# read models to paraview
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


# remove number from string tail
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
        gd = GroupTimeSteps(Input=reader)
        RenameSource("{}_list".format(trim_last_number(name)), gd)
        HideAll(cur_view)
        reader = gd
    gd_display = Show(reader, cur_view)
    ColorBy(gd_display, ['POINTS', 'tmp'])
    ColorBy(gd_display, ['POINTS', ''])
    cur_view.ResetCamera()
    Render()
    return reader

# create screenshots for given file from given cam_list    
def create_shot(file_list, cam_list, out_dir, pattern):
    cur_view = GetActiveViewOrCreate("RenderView")
    cur_source = read_and_render(file_list, cur_view)
    ss = ScreenShotHelper()
    for i in range(0, len(cam_list)):
        ss.take_shot(cur_view, cam_list[i], cur_source,
                     "{}/ss_{}_v{}.png".format(out_dir, pattern, i))

# read cam position from config file
def read_cam(case_name):
    case_file = os.path.join(dir_input, case_name, "config.txt")
    content = None
    with open(case_file) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content]
    str_lines = [line.split(", ") for line in str_list]
    return [[float(s) for s in item] for item in str_lines]


# setup active object
# get all concerned file names
# case/version/alg
file_dir = []
for ci in list_case:
    for vi in list_ver:
        file_dir.append([ci, vi, os.path.join(dir_output, ci, vi)])


#create shot
for case in file_dir:
    case_name = case[0]
    ver_name = case[1]
    case_files = case[2]
    cam_list = read_cam(case_name)
    for alg in list_alg:
        print("alg: {}".format(case_files))
        file_list = []
        file_alg = get_file(case_files, alg)
        if file_alg is None:
            if os.path.isdir(file_alg):
                file_list = get_file_list(file_alg)
            else:
                continue
        else:
            file_list.append(file_alg)
        create_shot(file_list, cam_list, os.path.join(dir_output, case_name, ver_name), alg)
