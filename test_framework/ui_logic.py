# -*- coding: utf-8 -*-
## @file ui_logic.py
## @brief ui signal/slot logitcs
## @author jiayanming

import os.path
import math
import sys
import datetime
import xml.etree.ElementTree as ET

sys.path.insert(0, r'c:/dev/py_scripts/')

import datetime
from test_framework import project_io
from test_framework import generate_docx

def get_checked_items(l_all, l_check):
    res = []
    for i in range(0, len(l_all)):
        if l_check == 0:
            continue
        res.append(l_all[i])
    return res


def generate_docx(filename, p_obj):
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    l_case = get_checked_items(p_obj._case, p_obj._dCaseCheck)
    l_alg = get_checked_items(p_obj._alg, p_obj._dAlgCheck)
    l_ver = get_checked_items(p_obj._ver, p_obj._dVerCheck)
    generate_docx(dir_i, dir_o, filename, l_case, l_alg, l_ver)


#def create_screen_shot(p_obj):
    
