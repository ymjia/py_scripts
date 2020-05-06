# -*- coding: utf-8 -*-
## @file time_stop.py
## @brief stop playing
## @author jiayanming

from paraview.simple import GetAnimationScene
ans = GetAnimationScene()
ans.Stop()
