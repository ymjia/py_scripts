# -*- coding: utf-8 -*-
## @file dental_desk_post.py
## @brief run dental desk post process sequence on given model
## @author jiayanming

import os.path
from paraview.simple import *
from paraview.simple import _active_objects

#setup active object
active_obj = _active_objects()
cur_view = active_obj.get_view()
cur_source = active_obj.get_source()
s_list = active_obj.get_selected_sources()

pxm = servermanager.ProxyManager();
s_name = os.path.splitext(pxm.GetProxyName("sources", cur_source))[0]

# Register data
regData = SnRegistration(Input=s_list)
RenameSource("{}_reg".format(s_name), regData)

# fusion
snReconstruction = SnReconstruction(regData)
snReconstruction.PointDistance = 0.08
snReconstruction.SplitThereshold = 14
RenameSource("{}_fusion".format(s_name), snReconstruction)

# create a new 'SnDenoiseBilateral'
snDenoiseBilateral = SnDenoiseBilateral(Input=snReconstruction)
snDenoiseBilateral.NormalIteration = 2
RenameSource("{}_denoise".format(s_name), snDenoiseBilateral)

# create a new 'SnSmooth'
snSmooth = SnSmooth(Input=snDenoiseBilateral)
RenameSource("{}_smooth".format(s_name), snSmooth)

# create a new 'SnRemoveSpike'
snRemoveSpike = SnRemoveSpike(Input=snSmooth)
RenameSource("{}_spike".format(s_name), snRemoveSpike)

# create a new 'SnRemoveSmallComponent'
snRemoveSmallComponent = SnRemoveSmallComponent(Input=snRemoveSpike)
snRemoveSmallComponent.ConnectionType = 'StrongConnection'
snRemoveSmallComponent.MinVNumber = 1000
snRemoveSmallComponent.MinFNumber = 1000
snRemoveSmallComponent.ConnectionRing = 3
RenameSource("{}_rm_small".format(s_name), snRemoveSmallComponent)

# create a new 'SnFillHole'
snFillHole = SnFillHole(Input=snRemoveSmallComponent)
snFillHole.MaxV = 0
snFillHole.MaxPerimeter = 20.0
RenameSource("{}_fill".format(s_name), snFillHole)

# create a new 'SnQEMSimp'
snQEMSimp = SnQEMSimp(Input=snFillHole)
RenameSource("{}_simp".format(s_name), snQEMSimp)

# create a new 'SnFlipEdge'
snFlipEdge = SnFlipEdge(Input=snQEMSimp)
RenameSource("{}_flip".format(s_name), snFlipEdge)

#show final result
HideAll(cur_view)
Show(snFlipEdge, cur_view)
ResetCamera(cur_view)

