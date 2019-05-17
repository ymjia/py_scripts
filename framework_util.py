# -*- coding: utf-8 -*-
## @file framework_util.py
## @brief utilize functions for test framework
## @author jiayanming
import os
import os.path
import math
import time
import datetime
from paraview.simple import *
from paraview.simple import _active_objects

# global variables
pxm = servermanager.ProxyManager()

# string operations===============
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


# file system operations==============
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
    if reader is None:
        return None
    if len(file_list) > 1:
        name = pxm.GetProxyName("sources", reader)
        gd = GroupTimeSteps(Input=reader)
        RenameSource("{}_list".format(trim_last_number(name)), gd)
        reader = gd
    return reader


# paraview operations ==========================
## @brief generate layouted views
## @note call before create views
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


## @brief add text annotation at left-top
def add_annotation(view, text, size):
    annot = Text()
    annot.Text = text
    dis = Show(annot, view)
    dis.FontFile = ''
    dis.FontSize = size
    dis.Color = [0.0, 0.0, 0.0]
    dis.Interactivity = 0
    dis.Shadow = 1


## @brief add time annotitions at right-bottom
def add_time_annotation(view, tfile):
    t = time.ctime(os.path.getmtime(tfile))
    file_time = str(datetime.datetime.strptime(t, "%a %b %d %H:%M:%S %Y"))
    cur_time = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    annot = Text()
    annot.Text = "Data time: {}\nCamera Time: {}".format(file_time, cur_time)
    dis = Show(annot, view)
    dis.WindowLocation = 'LowerRightCorner'
    dis.Justification = 'Right'
    dis.FontSize = 14
    dis.FontFile = ''
    dis.Color = [0.0, 0.0, 0.0]
    dis.Interactivity = 0
    dis.Shadow = 1


# load_file for given framework config(dir, case, alg, compare version_list)
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


# config operations ===========
## read config file, generate information for test framework
## @todo may use xml as config file

## @brief read user concerned case name list
def read_config_list(config_str, pattern):
    lc = len(config_str)
    lp = len(pattern)
    if lc < lp:
        return None
    if config_str[0:lp] != pattern:
        return None
    return config_str[lp+1:].split(" ")



def read_compare_config(file_config):
    if not os.path.exists(file_config):
        return None
    case_list = []
    ver_list = []
    alg_list = []
    content = None
    with open(file_config) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content]
    for line in str_list:
        if line[0:3] == "cas":
            case_list = read_config_list(line, "cas")
        elif line[0:3] == "ver":
            ver_list = read_config_list(line, "ver")
        elif line[0:3] == "alg":
            alg_list = read_config_list(line, "alg")
    return case_list, ver_list, alg_list
