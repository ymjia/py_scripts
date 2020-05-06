# -*- coding: utf-8 -*-
## @file rep_texture.py
## @brief load texture from file for current source
## @author jiayanming
import os.path
from paraview.simple import *
from paraview.simple import GetDisplayProperties
from paraview.simple import _active_objects

def set_texture(display, name):
    cur_t = display.Texture
    if cur_t is not None:
        return
    if name == "":
        return
    # if loaded
    is_loaded = False
    group = pxm.GetProxiesInGroup('textures')
    for key, t in group.items():
        if key[0] == name:
            is_loaded = True
            cur_t = t
            break
    # load picture as texture
    if not is_loaded:
        np = pxm.NewProxy("textures", "ImageTexture")
        fn = np.GetProperty('FileName')
        fn.SetElement(0, name)
        np.UpdateVTKObjects()
        pxm.RegisterProxy("textures", name, np)
        cur_t = np
    if cur_t is not None:
        display.Representation = 'Surface'
        display.BackfaceRepresentation = 'Surface'
        display.DiffuseColor = [1.0, 1.0, 1.0]
        display.Texture = cur_t


active_obj = _active_objects()
cur_source = active_obj.get_source()
cur_view = active_obj.get_view()

pxm = servermanager.ProxyManager()

# get mesh file name
name = ""
if hasattr(cur_source, 'FileNames') and cur_source.FileNames[0]:
    name = cur_source.FileNames[0]
if hasattr(cur_source, 'FileName'):
    name = cur_source.FileName

# set texture picture name
if not name == "":
    ext_list = [".jpg", ".png", ".bmp", ".ppm", ".tiff"]
    stem = os.path.splitext(name)[0]
    ext = ""
    for ei in ext_list:
        if os.path.exists(stem + ei):
            ext = ei
            break
    if ext == "":
        name = ""
    else:
        name = stem + ext

cur_display = GetDisplayProperties(cur_source, cur_view)

# set texture
set_texture(cur_display, name)
