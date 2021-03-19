# -*- coding: utf-8 -*-
## @file TableToCloud.py
## @brief programble filter to convert table to cloud
## @author jiayanming

from vtkmodules.vtkCommonDataModel import vtkDataSet
from vtkmodules.util.vtkAlgorithm import VTKPythonAlgorithmBase
from vtkmodules.numpy_interface import dataset_adapter as dsa

# new module for ParaView-specific decorators.
from paraview.util.vtkAlgorithm import smproxy, smproperty, smdomain

@smproxy.filter(label="Table To Cloud")
@smproperty.input(name="Input")
class HalfVFilter(VTKPythonAlgorithmBase):
    # the rest of the code here is unchanged.
    def __init__(self):
        VTKPythonAlgorithmBase.__init__(self)

    def RequestData(self, request, inInfo, outInfo):
        # get the first input.
        input0 = dsa.WrapDataObject(vtkDataSet.GetData(inInfo[0]))
        keys = input0.GetRowData().keys()
        vert = input0.GetRowData()['verts']
        pts = vtkPoints()
        pts.SetData(dsa.numpyTovtkDataArray(vert, 'Points'))

        # compute a value.
        data = input0.PointData["V"] / 2.0

        # add to output
        output = dsa.WrapDataObject(vtkDataSet.GetData(outInfo))
        output.GetPointData().SetPoints(pts)
        output.GetPointData().SetNormal(normals, 'Normals')
        #output.PointData.append(data, "V_half");
        return 1
