# -*- coding: utf-8 -*-
## @file compute_quality.py
## @brief example of use Filter:calculator
## @author jiayanming

# state file generated using paraview version 5.6.0
# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------
#### import the simple module from the paraview
from paraview.simple import *
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# Create a new 'SpreadSheet View'
# spreadSheetView1 = CreateView('SpreadSheetView')
# spreadSheetView1.SelectionOnly = 1
# spreadSheetView1.ColumnToSort = 'Result'
# spreadSheetView1.BlockSize = 1024
# spreadSheetView1.FieldAssociation = 'Cell Data'
# uncomment following to set a specific view size
# spreadSheetView1.ViewSize = [400, 400]

# ----------------------------------------------------------------
# restore active view
SetActiveView(renderView1)
# ----------------------------------------------------------------
# ----------------------------------------------------------------
# setup the data processing pipelines
# ----------------------------------------------------------------

# create a new 'ASC reader'
scanresult1asc = ASCreader(FileNames=['D:/data/_Dental/confirmed_points_181225/scan-result1.asc'])
scanresult1asc.NormalStartingPosition = 6
scanresult1asc.UVStartingPosition = 3

# create a new 'WrapPoints'
wrapPoints1 = WrapPoints(Input=scanresult1asc)
wrapPoints1.Scalars = ['POINTS', 'UV_coord']

# create a new 'Point Data to Cell Data'
pointDatatoCellData1 = PointDatatoCellData(Input=wrapPoints1)
pointDatatoCellData1.PassPointData = 1

# create a new 'Mesh Quality'
meshQuality1 = MeshQuality(Input=pointDatatoCellData1)

# create a new 'Calculator'
calculator1 = Calculator(Input=meshQuality1)
calculator1.AttributeType = 'Cell Data'
calculator1.ResultArrayName = 'sqrt'
calculator1.Function = 'sqrt(CustomProp)'

# create a new 'Calculator'
calculator2 = Calculator(Input=calculator1)
calculator2.AttributeType = 'Cell Data'
calculator2.Function = 'sqrt * Quality'

# create a new 'Threshold'
threshold1 = Threshold(Input=calculator2)
threshold1.Scalars = ['CELLS', 'Result']
threshold1.ThresholdRange = [0.0, 0.6]

# ----------------------------------------------------------------
# setup the visualization in view 'renderView1'
# ----------------------------------------------------------------

# show data from threshold1
threshold1Display = Show(threshold1, renderView1)
# ----------------------------------------------------------------
# setup the visualization in view 'spreadSheetView1'
# ----------------------------------------------------------------
# show data from threshold1
threshold1Display_1 = Show(threshold1, spreadSheetView1)

# ----------------------------------------------------------------
# finally, restore active source
SetActiveSource(meshQuality1)
# ----------------------------------------------------------------
