# -*- coding: utf-8 -*-
## @file registration.py
## @brief Registrate two triangle mesh
## put two target matrix in two views, adjust camera two roughly same position, then run this
## model in second view will be registed to the model in first view
## @author jiayanming

import os.path
import math
from paraview.simple import *
from paraview.simple import _active_objects
#from vtk import vtkMatrix4x4

pxm = servermanager.ProxyManager();

def get_source_in_view(slist, v):
    for si in slist:
        dp = servermanager.GetRepresentation(si, v)
        if not dp or dp.Visibility == 0: continue
        return si


def mt2str(vtkmt):
    res = ""
    for i in range(0, 4):
        for j in range(0, 4):
            res += "{} ".format(vtkmt.GetElement(i, j))
    return res


def copy_camera(v1, v2):
    v2.CameraPosition = v1.CameraPosition
    v2.CameraFocalPoint = v1.CameraFocalPoint
    v2.CenterOfRotation = v1.CenterOfRotation
    v2.CameraViewUp = v1.CameraViewUp

def get_rt(slist, ly):
    v_list = GetViewsInLayout(ly) #view in cur layout
    # get fix informations
    vfix = GetActiveView()
    sfix = get_source_in_view(slist, vfix)
    if sfix is None: return
    cfix = vfix.GetActiveCamera()
    mfix = mt2str(cfix.GetModelViewTransformMatrix())
    name_fix = os.path.splitext(pxm.GetProxyName("sources", sfix))[0]
    for vflt in v_list:
        if vflt == vfix: continue
        sflt = get_source_in_view(slist, vflt)
        cflt = vflt.GetActiveCamera()
        mflt = mt2str(cflt.GetModelViewTransformMatrix())
        # pass to ICP filter
        triMeshICP = SnTriMeshICP(FixMesh=sfix, FloatMesh=sflt)
        triMeshICP.FixMV = mfix
        triMeshICP.FltMV = mflt
        # rename source
        name_flt = os.path.splitext(pxm.GetProxyName("sources", sflt))[0]
        RenameSource("{}2{}".format(name_flt, name_fix), triMeshICP)
        Show(triMeshICP, vflt)
        Hide(sflt, vflt)
        copy_camera(vfix, vflt)
    Render()

active_obj = _active_objects()
cur_view = active_obj.get_view()
ly = GetLayout(cur_view)
s_list = GetSources().values() #all sources list
v_list = GetViewsInLayout(ly) #view in cur layout

rtl = get_rt(s_list, ly)
