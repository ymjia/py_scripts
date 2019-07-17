# -*- coding: utf-8 -*-
## @file ui_logic.py
## @brief ui signal/slot logitcs
## @author jiayanming

import os.path
import math
import sys
import datetime

import subprocess
from PyQt5.QtWidgets import QFileDialog
sys.path.insert(0, r'c:/dev/py_scripts/')

from test_framework.project_io import get_checked_items
from test_framework.generate_docx import generate_docx


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
    l_case = get_checked_items(p_obj._case, p_obj._sCaseCheck)
    l_alg = get_checked_items(p_obj._alg, p_obj._sAlgCheck)
    l_ver = get_checked_items(p_obj._ver, p_obj._sVerCheck)
    # write to file
    filename = "c:/tmp/ss_config.txt"
    line_case = "cas"
    for c in l_case:
        line_case = line_case + " {}".format(c)
    line_ver = "ver"
    for c in l_ver:
        line_ver = line_ver + " {}".format(c)
    line_alg = "alg"
    for c in l_alg:
        line_alg = line_alg + " {}".format(c)
    f_config = open(filename, "w")
    f_config.writelines(line_case)
    f_config.writelines(line_ver)
    f_config.writelines(line_alg)
    f_config.close()
    # run pvpython.exe
    exe_pvpython = ""
    proc_ss = subprocess.Popen(
        [exe_pvpython,
         dir_i, dir_o, f_config])
    proc_ss.wait()
    # create_screenshots(dir_i, dir_o, l_case, l_alg, l_ver)


# get file and set qle.text
def slot_get_path(qle):
    path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
    if path is not None and path != "":
        qle.setText(path)


def slot_get_file(qle, f_type):
    path = ""
    if f_type == "xml":
        path, _filter = QFileDialog.getOpenFileName(None, 'Open File', '', 'XML (*.xml)')
    else:
        path, _filter = QFileDialog.getOpenFileName(None, 'Open File', '', 'EXE (*.exe)')
    if path is not None and path != "":
        qle.setText(path)
