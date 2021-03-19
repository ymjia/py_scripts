# -*- coding: utf-8 -*-
## @file image_gaussian.py
## @brief process gaussian blur to image
## @author jiayanming
from paraview.simple import *
from paraview.simple import _active_objects
from vtk.numpy_interface import dataset_adapter as dsa

def create_gauss_filter(cur_source, img_type):
    gauss_filter = ProgrammableFilter(Input=cur_source)
    gauss_filter.Script = ''
    gauss_filter.RequestInformationScript = ''
    gauss_filter.RequestUpdateExtentScript = ''
    gauss_filter.PythonPath = ''

    # Properties modified on gauss_filter
    gauss_filter.Script = """import cv2
import numpy
from vtk.numpy_interface import dataset_adapter as dsa
pdi = self.GetInputDataObject(0,0)
pdo = self.GetOutputDataObject(0)
#pdo.CopyAttributes(pdi)
snp = dsa.WrapDataObject(pdi)
pix = snp.PointData['{}']
smooth = cv2.GaussianBlur(pix,(5,5),0)
vdarr = dsa.numpyTovtkDataArray(smooth, name='GaussianBlur')
im_out = self.GetImageDataOutput()
im_out.GetPointData().AddArray(vdarr)""".format(img_type)
    gauss_filter.RequestInformationScript = ''
    gauss_filter.RequestUpdateExtentScript = ''
    gauss_filter.CopyArrays = 0
    gauss_filter.PythonPath = ''
    return gauss_filter


active_obj = _active_objects()
cur_view = active_obj.get_view()
cur_source = active_obj.get_source()

# create a new 'Programmable Filter'
img_arr_name = "None"
sd = servermanager.Fetch(cur_source)
res_filter = None
if not sd.IsA("vtkImageData"):
    print("Selected source is not A Image")
else:
    pd = sd.GetPointData()
    pd_arr = [pd.GetArrayName(i) for i in range(0, pd.GetNumberOfArrays())]
    if 'PNGImage' in pd_arr:
        img_arr_name = "PNGImage"
    elif 'BMPImage' in pd_arr:
        img_arr_name = "BMPImage"
    elif 'JPEGImage' in pd_arr:
        img_arr_name = "JPEGImage"
    else:
        img_arr_name = "None"
    if img_arr_name != "None":
        res_filter = create_gauss_filter(cur_source, img_arr_name)
    
if res_filter is not None:
    dp = Show(res_filter, cur_view)
    ColorBy(dp, ('POINTS', 'GaussianBlur', 'Magnitude'))
    Hide(cur_source, cur_view)
