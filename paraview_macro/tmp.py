# -*- coding: utf-8 -*-
## @file compare_data.py
## @brief set compare views for selected sources, most support number: 6
## @author jiayanming

import os.path
import math
from paraview.simple import *
from paraview.simple import _active_objects
from numpy.linalg import inv
from numpy import matmul
from numpy import *
#from vtk import vtkMatrix4x4

pxm = servermanager.ProxyManager();
active_obj = _active_objects()
cur_view = active_obj.get_view()
cur_source = active_obj.get_source()
ly = GetLayout(cur_view)
s_list = GetSources().values() #all sources list


# def get_cur_matrix(cur_view):
#     [w, h]=cur_view.GetRenderer().GetSize();
#     camera = cur_view.GetActiveCamera();
#     [n, f] = camera.GetClippingRange();
#     print(f,n);
#     return camera.GetProjectionTransformMatrix(float(w)/float(h), -1.0, 1.0);

#iIntrinsic = vtk.vtkMatrix4x4();
#A.Invert(A, iIntrinsic);


######################

# from docx import Document
# from docx.shared import Inches

# document = Document()

# document.add_paragraph('对比', style='List Bullet')
# document.save('d:/tmp/compare.docx')
#setup active object



# create a new 'Group Datasets'
gd = GroupDatasets(Input=s_list)
# show data in view
HideAll(cur_v)
gd_display = Show(gd, cur_v)
ColorBy(gd_display, ['POINTS', 'tmp'])#trick direct use of ['POINT', ''] does not work
ColorBy(gd_display, ['POINTS', ''])
cur_v.Update()
