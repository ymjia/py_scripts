# -*- coding: utf-8 -*-
## @file framework_util.py
## @brief utilize functions for test framework
## @note only used in pvpython
## @author jiayanming
import os
import os.path
from pathlib import Path
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
support_ext = [".asc", ".rge", ".obj", ".stl", ".ply", ".srge", ".bin", ".tb"]


def get_file_list(folder):
    res = []
    for name in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, name)):
            continue
        ext = os.path.splitext(name)[1].casefold()
        if not any(ext in e for e in support_ext):
            continue
        res.append(os.path.join(folder, name))
    return res


# read file name with stem in folder, return *list*
def get_file(folder, stem):
    stem = stem.casefold()
    if not os.path.exists(folder):
        return None
    full_path = os.path.join(folder, stem)
    res = []
    if os.path.isdir(full_path):
        res = get_file_list(full_path)
    if len(res) > 0:
        return res
    cur_root = str(Path(full_path).parent)
    for f in os.listdir(cur_root):
        cur_stem, cur_ext = os.path.splitext(f)
        if cur_stem.casefold() == stem and cur_ext in support_ext:
            return [os.path.join(folder, f)]
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
    if s_num == 1:
        return [0]
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


def add_light_to_view(cur_view, append=False):
    if not append and len(cur_view.AdditionalLights) >= 1:
        return
    light = AddLight(view=cur_view)
    # Properties modified on light1
    light.Coords = 'Camera'
    light.Type = 'Directional'
    light.Position = [-1.0, 1.0, 1.0]
    light.FocalPoint = [1.0, -1.0, 0.0]
    # Properties modified on light
    light.Intensity = 0.5


## @brief add text annotation at left-top
def add_annotation(view, text, size):
    annot = Text()
    annot.Text = text
    dis = Show(annot, view)
    dis.FontFile = ''
    dis.FontSize = size
    dis.Color = [1.0, 1.0, 0.498]
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
    dis.Color = [1.0, 1.0, 0.498]
    dis.Interactivity = 0
    dis.Shadow = 1


# load_file for given framework config(dir, case, alg, compare version_list)
# *deprecated* 20200507, stay here for backward compatibility
def load_state_files(dir_input, dir_output, case, alg, list_v): 
    # get source list
    list_dir = []
    list_annot = []
    list_source = []
    for v in list_v:
        dir_source = ""
        if v == "input":
            dir_source = os.path.join(dir_input, case)
            list_dir.append(dir_source)
            list_annot.append("{}_input".format(case))
            list_source.append(get_file(dir_input, case))
        else:
            dir_source = os.path.join(dir_output, case, v)
            list_dir.append(dir_source)
            list_annot.append("{}_{}_{}".format(case, v, alg))
            list_source.append(get_file(dir_source, alg))
    # create layout before create view
    l = CreateLayout('{}_{}'.format(case, alg))
    assign_file_to_layout(list_annot, list_source, l)


def load_state_files_v1(dir_input, dir_output, case, list_v, list_alg, compare_type = "Versions", has_input=False):
    # get source list
    list_dir = []
    list_annot = []
    list_source = []
    if has_input:
        dir_source = os.path.join(dir_input, case)
        list_dir.append(dir_source)
        list_annot.append("{}_input".format(case))
        list_source.append(get_file(dir_input, case))

    for v in list_v:
        dir_source = ""
        if v == "input":
            continue
        for alg in list_alg:
            dir_source = os.path.join(dir_output, case, v)
            list_dir.append(dir_source)
            list_annot.append("{}_{}_{}".format(case, v, alg))
            list_source.append(get_file(dir_source, alg))
    # create layout before create view
    l = CreateLayout('{}_{}'.format(case, alg))
    assign_file_to_layout(list_annot, list_source, l)


def assign_file_to_layout(list_annot, list_source, l):
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
## @brief configuration for current session
class SessionConfig:
    def __init__(self):
        self.list_case = []
        self.list_ver = []
        self.list_alg = []
        self.config_map = {}
        # parameter for hausdorff
        self.config_map["hd_nominal_dist"] = "0.03"
        self.config_map["hd_critical_dist"] = "0.05"
        self.config_map["hd_max_dist"] = "0.3"
        self.config_map["hd_single_color"] = "True"
        self.config_map["hd_camera_angle"] = "4"
        # parameter for screenshot
        self.config_map["ss_force_update"] = "False"
        self.config_map["rep_specular"] = "True"
        self.config_map["view_width"] = "1024"
        self.config_map["view_height"] = "768"
        self.config_map["transparent_background"] = "False"

    def config_val(self, key_str, default_val):
        if key_str in self.config_map:
            return self.config_map[key_str]
        return default_val

    def read_config(self, filename):
        if not os.path.exists(filename):
            print("Warning! config file {} does not exists".format(filename))
            return False
        content = None
        with open(filename, encoding='utf-8') as f:
            content = f.readlines()
        lines = [l.strip() for l in content]
        if len(lines) < 3:
            print("Warning! Invalid config file {}".format(filename))
            return False
        # fix part
        if lines[0][0:3] != "cas" or lines[1][0:3] != "ver" or lines[2][0:3] != "alg":
            print("Warning! Invalid config file {}".format(filename))
            return False
        self.list_case = lines[0].split(" ")[1:].copy()
        self.list_ver = lines[1].split(" ")[1:].copy()
        self.list_alg = lines[2].split(" ")[1:].copy()
        # optional part
        for i in range(4, len(lines)):
            l_couple = lines[i].split(" ")
            if len(l_couple) != 2:
                continue
            self.config_map[l_couple[0]] = l_couple[1]
        return True

    def write_config(self, filename):
        f_config = open(filename, "w", encoding='utf-8')
        f_config.writelines("cas {}\n".format(" ".join(map(str, self.list_case))))
        f_config.writelines("ver {}\n".format(" ".join(map(str, self.list_ver))))
        f_config.writelines("alg {}\n".format(" ".join(map(str, self.list_alg))))
        for key, val in self.config_map.items():
            f_config.writelines("{} {}\n".format(key, val))
        f_config.close()

    def print_config(self):
        print("cas {}".format(" ".join(map(str, self.list_case))))
        print("ver {}".format(" ".join(map(str, self.list_ver))))
        print("alg {}".format(" ".join(map(str, self.list_alg))))
        for key, val in self.config_map.items():
            print("{} {}".format(key, val))



def fill_list(res, idx, in_list):
    if isinstance(in_list, int) or isinstance(in_list, float):
        res.append(in_list)
        return 1
    ac = len(in_list)
    res[idx: idx + len(in_list)] = in_list[:]
    return ac

## @brief camera info save/load/generate object
class CameraObject:
    def __init__(self):
        self.CameraFocalPoint = [0.0, 0.0, 1.0]
        self.CameraParallelProjection = 0
        self.CameraParallelScale = 20.0
        self.CameraPosition = [0.0, 0.0, 0.0]
        self.CameraViewAngle = 30.0
        self.CameraViewUp = [0.0, 0.0, 0.0]

    ## @brief create standard camera info from object
    ## @param type_str x+ x- y+ y- z+ z-
    def create_default_cam_angle(self, s, type_str):
        (xmin, xmax, ymin, ymax, zmin, zmax) = s.GetDataInformation().GetBounds()
        xmid = (xmin + xmax) / 2
        ymid = (ymin + ymax) / 2
        zmid = (zmin + zmax) / 2
        xdelta = xmax - xmin
        ydelta = ymax - ymin
        zdelta = zmax - zmin

        if len(type_str) < 2:
            type_str = "x+"
        position_ratio = math.tan(self.CameraViewAngle / 300.0 * math.pi)
        # reset camera
        self.CameraViewUp = [0.0, 0.0, 0.0]
        self.CameraFocalPoint = [xmid, ymid, zmid]
        self.CameraPosition = [xmid, ymid, zmid]

        # get camera info
        if type_str[0] == 'y':
            self.CameraViewUp[2] = 1
            camera_move = (xdelta + zdelta) / 2 / position_ratio
            if type_str[1] == '+':
                self.CameraPosition[1] = self.CameraPosition[1] - camera_move
            else:
                self.CameraPosition[1] = self.CameraPosition[1] + camera_move
        elif type_str[0] == 'z':
            self.CameraViewUp[1] = 1
            camera_move = (xdelta + ydelta) / 2 / position_ratio
            if type_str[1] == '+':
                self.CameraPosition[2] = self.CameraPosition[2] - camera_move
            else:
                self.CameraPosition[2] = self.CameraPosition[2] + camera_move
        else: # x
            self.CameraViewUp[2] = 1
            camera_move = (ydelta + zdelta) / 2 / position_ratio
            if type_str[1] == '+':
                self.CameraPosition[0] = self.CameraPosition[0] - camera_move
            else:
                self.CameraPosition[0] = self.CameraPosition[0] + camera_move

    ## @brief create camera in 4 phase
    ## @param type_str x+y+, x+y-, x-y+, x-y-
    def create_4_cam_angle(self, s, type_str):
        (xmin, xmax, ymin, ymax, zmin, zmax) = s.GetDataInformation().GetBounds()
        xmid = (xmin + xmax) / 2
        ymid = (ymin + ymax) / 2
        zmid = (zmin + zmax) / 2
        xdelta = xmax - xmin
        ydelta = ymax - ymin
        zdelta = zmax - zmin
        if len(type_str) < 4:
            type_str = "x+y+"
        position_ratio = math.tan(self.CameraViewAngle / 200.0 * math.pi)
        camera_move = (xdelta + ydelta) / float(2) / position_ratio / math.sqrt(3)
        # reset camera
        self.CameraViewUp = [0.0, 0.0, 1.0]
        self.CameraFocalPoint = [xmid, ymid, zmid]
        self.CameraPosition = [xmid, ymid, zmid + camera_move]
        # x
        if type_str[1] == "+":
            self.CameraPosition[0] = xmid + camera_move
        else:
            self.CameraPosition[0] = xmid - camera_move
        # y
        if type_str[3] == "+":
            self.CameraPosition[1] = ymid + camera_move
        else:
            self.CameraPosition[1] = ymid - camera_move


    ## @brief set view camera to current object
    def set_camera(self, v):
        v.CameraFocalPoint = self.CameraFocalPoint.copy()
        v.CameraParallelProjection = int(self.CameraParallelProjection)
        v.CameraParallelScale = self.CameraParallelScale
        v.CameraPosition = self.CameraPosition.copy()
        v.CameraViewAngle = self.CameraViewAngle
        v.CameraViewUp = self.CameraViewUp.copy()
        v.Update()

    ## @brief fill camera info from view
    def get_camera(self, v):
        self.CameraFocalPoint = v.CameraFocalPoint.copy()
        self.CameraParallelProjection = v.CameraParallelProjection
        self.CameraParallelScale = v.CameraParallelScale
        self.CameraPosition = v.CameraPosition.copy()
        self.CameraViewAngle = v.CameraViewAngle
        self.CameraViewUp = v.CameraViewUp.copy()

    def generate_camera_str(self):
        camera_pos = []
        idx = 0
        idx += fill_list(camera_pos, idx, self.CameraFocalPoint)
        idx += fill_list(camera_pos, idx, self.CameraParallelProjection)
        idx += fill_list(camera_pos, idx, self.CameraParallelScale)
        idx += fill_list(camera_pos, idx, self.CameraPosition)
        idx += fill_list(camera_pos, idx, self.CameraViewAngle)
        idx += fill_list(camera_pos, idx, self.CameraViewUp)
        clip_str = str(camera_pos[0])
        for i in range(1, len(camera_pos)):
            clip_str += ", {}".format(camera_pos[i])
        return clip_str

    def read_camera_from_str(self, cam_str):
        str_list = cam_str.split(", ")
        try:
            if len(str_list) == 12:
                flt_list = [float(s) for s in str_list]
                self.CameraFocalPoint = flt_list[0:3]
                self.CameraParallelProjection = flt_list[3]
                self.CameraParallelScale = flt_list[4]
                self.CameraPosition = flt_list[5:8]
                self.CameraViewAngle = flt_list[8]
                self.CameraViewUp = flt_list[9:12]
                return True
            else:
                return False
        except ValueError:
            return False
