# -*- coding: utf-8 -*-
## @file create_screenshots.py
## @brief create screenshots for mesh in given position
## @author jiayanming
import os
import os.path
import sys
import math
import time
import datetime
from paraview.simple import *
from paraview.simple import _active_objects
dir_py_module = os.path.join(os.getcwd(), "..", "Sn3D_plugins", "scripts", "pv_module")
sys.path.append(dir_py_module)
from framework_util import *


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
        v_size = view.ViewSize
        view.Update()
        SaveScreenshot(filename, view, ImageResolution=v_size, TransparentBackground=0)


# read file or file list and render in given view
def read_and_render(file_list, v):
    HideAll(v)
    reader = read_files(file_list)
    reader_display = Show(reader, v)
    reader_display.ColorArrayName = [None, '']
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
    add_time_annotation(v, f)
    v.Update()
    return reader


# create screenshots for given file from given cam_list    
def create_shot(file_list, cam_list, out_dir, pattern):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    cur_view = GetActiveViewOrCreate("RenderView")
    cur_view.ViewSize = [1024, 768]
    add_light_to_view(cur_view, False)
    cur_view.CenterAxesVisibility = 0
    cur_source = read_and_render(file_list, cur_view)
    ss = ScreenShotHelper()
    for i in range(0, len(cam_list)):
        ss.take_shot(cur_view, cam_list[i],
                     "{}/ss_{}_v{}.png".format(out_dir, pattern, i))
    Delete(cur_source)
    del cur_source

# read cam position from config file
def read_cam(case_file):
    if not os.path.exists(case_file):
        return None
    content = None
    with open(case_file) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content if len(l) > 20]
    str_lines = [line.split(", ") for line in str_list]
    return [[float(s) for s in item] for item in str_lines if len(item) == 12]

# if data_file newer than ss_file, need update
def ss_need_update(file_list, file_cam, out_dir, pattern):
    file_pic = os.path.join("{}/ss_{}_v0.png".format(out_dir, pattern))
    if not os.path.exists(file_pic):
        return True
    time_config = os.path.getmtime(file_cam)
    time_data = os.path.getmtime(file_list[0])
    time_pic = os.path.getmtime(file_pic)
    if time_config > time_pic: # new cam config
        return True
    if time_data > time_pic: # new data
        return True
    return False


# read configuration
def create_screenshots(dir_input, dir_output, list_case, list_alg, list_ver):
    # case/version/alg
    file_dir = []
    for ci in list_case:
        for vi in list_ver:
            file_dir.append([ci, vi, os.path.join(dir_output, ci, vi)])

    #create shot
    for item in file_dir:
        case_name = item[0]
        ver_name = item[1]
        case_files = item[2]
        cam_file = os.path.join(dir_input, case_name, "config.txt")
        cam_list = read_cam(cam_file)
        if cam_list is None or len(cam_list) < 1:
            continue
        if ver_name == "input":
            i_list = get_file(dir_input, case_name)
            pic_out_dir = os.path.join(dir_output, case_name, "input")
            if not ss_need_update(i_list, cam_file, pic_out_dir , "input"):
                continue
            create_shot(i_list, cam_list, pic_out_dir, "input")
        else:
            for alg in list_alg:
                file_list = get_file(case_files, alg)
                if file_list is None or len(file_list) < 1:
                    continue
                pic_out_dir = os.path.join(dir_output, case_name, ver_name)
                if not ss_need_update(file_list, cam_file, pic_out_dir, alg):
                    continue
                print("Updating screenshots for {}/{}/{}".format(case_name, ver_name, alg))
                create_shot(file_list, cam_list, pic_out_dir , alg)


def create_screenshots_wrap(dir_input, dir_output, file_config):
    # data to be compared
    # get all concerned file names
    list_case, list_ver, list_alg = read_compare_config(file_config)
    create_screenshots(dir_input, dir_output, list_case, list_alg, list_ver)


if __name__ == "__main__":
    dir_input = sys.argv[1]
    dir_output = sys.argv[2]
    file_config = sys.argv[3]
    create_screenshots_wrap(dir_input, dir_output, file_config)
