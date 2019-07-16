# -*- coding: utf-8 -*-
## @file ui_logic.py
## @brief ui signal/slot logitcs
## @author jiayanming

import os.path
import math
import sys
import datetime
import xml.etree.ElementTree as ET
import datetime
sys.path.insert(0, r'c:/dev/py_scripts/')


from test_framework import project_io
from test_framework.generate_docx import generate_docx
from test_framework.create_screenshots import create_screenshots

def get_checked_items(l_all, l_check):
    res = []
    for i in range(0, len(l_all)):
        if l_check == 0:
            continue
        res.append(l_all[i])
    return res


def slot_generate_docx(filename, p_obj):
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    l_case = get_checked_items(p_obj._case, p_obj._dCaseCheck)
    l_alg = get_checked_items(p_obj._alg, p_obj._dAlgCheck)
    l_ver = get_checked_items(p_obj._ver, p_obj._dVerCheck)
    generate_docx(dir_i, dir_o, filename, l_case, l_alg, l_ver)


def slot_create_screenshots(p_obj):
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    l_case = get_checked_items(p_obj._case, p_obj._dCaseCheck)
    l_alg = get_checked_items(p_obj._alg, p_obj._dAlgCheck)
    l_ver = get_checked_items(p_obj._ver, p_obj._dVerCheck)
    create_screenshots(dir_i, dir_o, l_case, l_alg, l_ver)
