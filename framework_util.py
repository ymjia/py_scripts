# -*- coding: utf-8 -*-
## @file open_case.py
## @brief open case file from test framework
## @author jiayanming
import os
import os.path
import math
import time
import datetime
from paraview.simple import *
from paraview.simple import _active_objects


dir_in = "d:/data/test_framwork/output/"


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
    return reader

def generate_view(l, s_num):
    # view positions in layout
    l_pos = []
    # split layout and store positions
    if s_num == 2:
        pos = l.SplitHorizontal(0, 0.5)
        l_pos = [pos, pos + 1]
    # 3 view horizontally
    if s_num == 3:
        pos = l.SplitHorizontal(0, 0.33)
        pos2 = l.SplitHorizontal(pos + 1, 0.5)
        l_pos = [pos, pos2, pos2 + 1]
    # 2 X 2
    if s_num == 4:
        tmp = l.SplitHorizontal(0, 0.5)
        pos0 = l.SplitVertical(tmp, 0.5)
        pos1 = l.SplitVertical(tmp + 1, 0.5)
        l_pos = [pos0, pos0 + 1, pos1, pos1 + 1]
    # 2 X 2 + 1 / 3 X 2
    if s_num == 5 or s_num == 6:
        # split horizontally to 3
        tmp1 = l.SplitHorizontal(0, 0.33)
        tmp2 = l.SplitHorizontal(tmp1 + 1, 0.5)
        tmp3 = tmp2 + 1
        pos0 = l.SplitVertical(tmp1, 0.5)
        pos1 = l.SplitVertical(tmp2, 0.5)
        pos2 = tmp3
        if s_num == 6:
            # split last one
            pos2 = l.SplitVertical(tmp3, 0.5)
        l_pos = [pos0, pos0 + 1, pos1, pos1 + 1, pos2]
        if s_num == 6:
            l_pos.append(pos2 + 1)
    return l_pos


# generate paraview project for given data
def load_state_files(dir_in, case, alg, list_v):
    # get source list
    list_dir = [os.path.join(dir_in, case, v) for v in list_v]
    list_annot = ["{}_{}_{}".format(case, v, alg) for v in list_v]
    # read file
    list_source = [get_file(d, alg) for d in list_dir]
    list_proxy = []
    for si in range(0, len(list_source)):
        reader = read_files(list_source[si])
        if reader is None:
            print("Fail reading file: {}".format(list_source[si]))
            continue
        RenameSource(list_annot[si], reader)
        list_proxy.append(reader)
    if len(list_source) != len(list_proxy):
        print("Error: target file lost!")
        return
    # create layout before create view
    l = CreateLayout('{}_{}'.format(case, alg))
    l_pos = generate_view(l, len(list_proxy))
    # create view
    list_view = [CreateRenderView(False, registrationName=annot) for annot in list_annot]
    # show sources in view
    v0 = list_view[0]
    for i in range(0, len(l_pos)):
        cur_v = list_view[i]
        l.AssignView(l_pos[i], cur_v)
        Show(list_proxy[i], list_view[i])
        if i != 0:
            time_str = time.mktime(datetime.datetime.now().timetuple())
            AddCameraLink(v0, cur_v, "l{}{}{}".format(time_str, 0, i))
    SetActiveView(v0)
    v0.ResetCamera()
    Render()

# input data read from config file
list_case = ["case1", "case2"]
# versions to be compared
list_ver = ["v11", "v12"]
# compare alg list
list_alg = ["smooth", "merge"]

load_state_files(dir_in, "case1", "smooth", ["v11", "v12"])
load_state_files(dir_in, "case2", "merge", ["v11", "v12"])
