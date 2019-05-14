# -*- coding: utf-8 -*-
## @file get_camera.py
## @brief record camera position of current view
## @author jiayanming
from tkinter import Tk
from paraview.simple import *

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
for i in range(1, len(camera_pos)):
    clip_str += ", {}".format(camera_pos[i])
r = Tk()
r.withdraw()
r.clipboard_clear()
r.clipboard_append(clip_str)
r.update()
r.destroy()
