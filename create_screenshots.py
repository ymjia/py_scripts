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


# get all file from folder except subdir
def get_file_list(folder):
    return [os.path.join(folder, name) for name in os.listdir(folder)
            if not os.path.isdir(os.path.join(folder, name))]

# read file name with stem in folder, return *list*
def get_file(folder, stem):
    if not os.path.exists(folder):
        return None
    for f in os.listdir(folder):
        cur_stem = os.path.splitext(f)[0]
        if cur_stem == stem:
            find_res = os.path.join(folder, f)
            if os.path.isdir(find_res):
                return get_file_list(find_res)
            else:
                return [find_res]
    return None

# read models to paraview
def read_files(file_list):
    if not isinstance(file_list, list):
        print("Error: read file input not list: {}".format(file_list))
        return None
    if len(file_list) < 1:
        return None
    reader = OpenDataFile(file_list)
    if reader is None: return None
    #RenameSource(stem, reader)
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
    if idx == c_num or idx == 1:
        return name_str
    return str(name_str[:-1 * idx + 1])


dir_input = "c:/data/test_framwork/input/"
dir_output = "c:/data/test_framwork/output/"
# versions to be compared
list_ver = ["v11", "v12"]
# input data
list_case = ["case1", "case2"]
# compare alg list
list_alg = ["smooth", "merge"]


# class for screenshots
class ScreenShotHelper:
    def __init__(self):
        paraview.simple._DisableFirstRenderCameraReset()

    # fill camera variable from number list
    def fill_var(self, in_list, idx, var):
        if isinstance(var, int) or isinstance(var, float):
            var = in_list[idx]
            return 1
        ac = len(var)
        var[:] = in_list[idx: idx + len(var)]
        return ac

    def set_camera(self, v, cam):
        idx = 0
        idx += self.fill_var(cam, idx, v.CameraFocalPoint)
        idx += self.fill_var(cam, idx, v.CameraParallelProjection)
        idx += self.fill_var(cam, idx, v.CameraParallelScale)
        idx += self.fill_var(cam, idx, v.CameraPosition)
        idx += self.fill_var(cam, idx, v.CameraViewAngle)
        idx += self.fill_var(cam, idx, v.CameraViewUp)

    def take_shot(self, view, cam, filename):
        self.set_camera(view, cam)
        view.Update()
        v_size = view.ViewSize
        SaveScreenshot(filename, view, ImageResolution=v_size, TransparentBackground=1)

def add_annotation(view, text, size):
    annot = Text()
    annot.Text = text
    dis = Show(annot, view)
    dis.FontFile = ''
    dis.FontSize = 2
    dis.FontSize = size
    dis.Color = [0.0, 0.0, 0.0]
    dis.Interactivity = 0
    dis.Shadow = 1


# read file or file list and render in given view
def read_and_render(file_list, v):
    reader = read_files(file_list)
    if reader is None:
        return None

    if len(file_list) > 1:
        name = pxm.GetProxyName("sources", reader)
        gd = GroupTimeSteps(Input=reader)
        RenameSource("{}_list".format(trim_last_number(name)), gd)
        reader = gd
    HideAll(v)
    gd_display = Show(reader, v)
    ColorBy(gd_display, ['POINTS', 'tmp'])
    ColorBy(gd_display, ['POINTS', ''])
    v.ResetCamera()
    # add anotation
    f = file_list[0]
    path, filename = os.path.split(f)
    if len(file_list) > 1: # file list, fetch parent dir
        path, filename = os.path.split(path)
    stem = trim_last_number(os.path.splitext(filename)[0])
    path, ver = os.path.split(path)
    path, case = os.path.split(path)
    add_annotation(v, "{}_{}_{}".format(case, ver, stem), 28)
    #v.Update()
    Render()
    return reader

# create screenshots for given file from given cam_list    
def create_shot(file_list, cam_list, out_dir, pattern):
    cur_view = GetActiveViewOrCreate("RenderView")
    cur_source = read_and_render(file_list, cur_view)
    ss = ScreenShotHelper()
    for i in range(0, len(cam_list)):
        ss.take_shot(cur_view, cam_list[i],
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
        file_list = get_file(case_files, alg)
        if file_list is None:
            continue
        create_shot(file_list, cam_list, os.path.join(dir_output, case_name, ver_name), alg)
