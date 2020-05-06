# -*- coding: utf-8 -*-
## @file dental_intro_post.py
## @brief run dental intra post process sequence on given model
## @author jiayanming

import os.path
from paraview.simple import *
from paraview.simple import _active_objects

#setup active object
active_obj = _active_objects()
cur_view = active_obj.get_view()
cur_source = active_obj.get_source()

pxm = servermanager.ProxyManager();
s_name = os.path.splitext(pxm.GetProxyName("sources", cur_source))[0]

# create a new 'SnDenoiseBilateral'
snDenoiseBilateral = SnDenoiseBilateral(Input=cur_source)
snDenoiseBilateral.NormalIteration = 2

# create a new 'SnSmooth'
snSmooth = SnSmooth(Input=snDenoiseBilateral)

# create a new 'SnRemoveSpike'
snRemoveSpike = SnRemoveSpike(Input=snSmooth)

# create a new 'SnRemoveSmallComponent'
snRemoveSmallComponent = SnRemoveSmallComponent(Input=snRemoveSpike)
snRemoveSmallComponent.ConnectionType = 'StrongConnection'
snRemoveSmallComponent.MinVNumber = 1000
snRemoveSmallComponent.MinFNumber = 1000
snRemoveSmallComponent.ConnectionRing = 3

# create a new 'SnFillHole'
snFillHole = SnFillHole(Input=snRemoveSmallComponent)
snFillHole.MaxV = 0
snFillHole.MaxPerimeter = 20.0

# create a new 'SnQEMSimp'
snQEMSimp = SnQEMSimp(Input=snFillHole)

# create a new 'SnFlipEdge'
snFlipEdge = SnFlipEdge(Input=snQEMSimp)

HideAll(cur_view)
Show(snFlipEdge, cur_view)
ResetCamera(cur_view)
Render()
