# -*- coding: utf-8 -*-
## @file time_prev.py
## @brief previous time step
## @author jiayanming

from paraview.simple import GetAnimationScene
ans = GetAnimationScene()
ans.GoToPrevious()
