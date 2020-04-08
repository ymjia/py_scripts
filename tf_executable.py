# -*- coding: utf-8 -*-
## @file tf_executable.py
## @brief test framework standalone executable
## @author jiayanming

import sys
import os
import datetime
from pathlib import Path
sys.path.insert(0, os.getcwd())
from test_framework import ui_logic
from test_framework import generate_docx
def create_screenshots(file_config):
    total_num = call_pvpython(exe_pvpython, l_case, ['__hausdorff'], [], dir_i, dir_o)


def deviation_report(dir_input):
    if not os.path.isdir(dir_input):
        print("Error! Input Argument {} is not a directory".format(dir_input))
    case_name = os.path.basename(dir_input)
    l_case = [case_name]
    dir_in = str(Path(dir_input).parent)
    dir_out = os.path.join(dir_in, "__output")
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)
    total_num = ui_logic.call_pvpython(exe_pvpython, l_case, ['__hausdorff'], [], dir_in, dir_out)

    # generate docx
    str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    doc_name_final = "Deviation_report_{}.docx".format(str_time)
    dir_doc = os.path.join(dir_out, "doc")
    if not os.path.exists(dir_doc):
        os.makedirs(dir_doc)
    file_save = os.path.join(dir_doc, doc_name_final)
    l_ver = ["hausdorff_A2B", "hausdorff_B2A"]
    l_alg = ["__hd"] # reserved alg_name for hausdorff dist
    gd = generate_docx.DocxGenerator(dir_in, dir_out, l_case, l_ver, l_alg)
    gd.generate_docx(file_save, "")


exe_pvpython = "c:/ParaView/bin/pvpython.exe"
dir_test = "C:/data/test_framework/management/project1/input/case1"
deviation_report(dir_test)
