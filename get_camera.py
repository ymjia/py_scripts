# -*- coding: utf-8 -*-
## @file get_camera.py
## @brief record camera position of current view
## @author jiayanming
import os
import sys
from tkinter import Tk
from paraview.simple import *
dir_pv_module = os.path.join(os.getcwd(), "..", "SN3D_plugins", "scripts", "pv_module")
sys.path.append(dir_pv_module)
from copy_display import get_view_source


def fill_list(res, idx, in_list):
    if isinstance(in_list, int) or isinstance(in_list, float):
        res.append(in_list)
        return 1
    ac = len(in_list)
    res[idx: idx + len(in_list)] = in_list[:]
    return ac
v = GetActiveView()

camera_pos = []
idx = 0
idx += fill_list(camera_pos, idx, v.CameraFocalPoint)
idx += fill_list(camera_pos, idx, v.CameraParallelProjection)
idx += fill_list(camera_pos, idx, v.CameraParallelScale)
idx += fill_list(camera_pos, idx, v.CameraPosition)
idx += fill_list(camera_pos, idx, v.CameraViewAngle)
idx += fill_list(camera_pos, idx, v.CameraViewUp)

print(*camera_pos, sep=",")

clip_str = str(camera_pos[0])
# for i in range(1, len(camera_pos)):
#     clip_str += ", {}".format(camera_pos[i])
# r = Tk()
# r.withdraw()
# r.clipboard_clear()
# r.clipboard_append(clip_str)
# r.update()
# r.destroy()


def get_source_dir(s):
    if not hasattr(s, "FileNames"):
        return ""
    f_list = s.FileNames
    if len(f_list) < 1:
        return ""
    return os.path.dirname(f_list[0])


# change txt config file
s_list = GetSources().values()
cur_source = get_view_source(s_list, v)
s_dir = get_source_dir(cur_source)
if s_dir != "" and os.path.exists(s_dir):
    file_config = os.path.join(s_dir, "config.txt")
    if os.path.exists(file_config):
        f = open(file_config, "a")
        f.writelines(clip_str + "\n")
        f.close()
