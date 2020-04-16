# -*- coding: utf-8 -*-
## @file tf_executable.py
## @brief test framework standalone executable
## @author jiayanming

import sys
import os
import datetime
from pathlib import Path
sys.path.insert(0, os.getcwd())
from test_framework.generate_docx import DocxGenerator
from test_framework.utils import SessionConfig
from test_framework.utils import g_config
from test_framework import create_screenshots


def deviation_report(dir_input):
    if not os.path.isdir(dir_input):
        print("Error! Input Argument {} is not a directory".format(dir_input))
    case_name = str(Path(dir_input).name)
    print("case_name: {}".format(case_name))
    sc = SessionConfig()
    sc.list_case = [str(case_name)]
    sc.list_ver = ['__hausdorff']
    sc.list_alg = []
    print(sc.list_case)
    dir_in = str(Path(dir_input).parent)
    dir_out = os.path.join(dir_input, "__output")
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)

    sc.dir_i = dir_in
    sc.dir_o = dir_out

    total_num = create_screenshots.create_hausdorff_shot(sc)

    # generate docx
    str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    doc_name_final = "Deviation_report_{}.docx".format(str_time)
    dir_doc = os.path.join(dir_out, "doc")
    if not os.path.exists(dir_doc):
        os.makedirs(dir_doc)
    file_save = os.path.join(dir_doc, doc_name_final)
    l_ver = ["hausdorff_A2B"]
    l_alg = ["__hd"] # reserved alg_name for hausdorff dist
    gd = DocxGenerator(dir_in, dir_out, sc.list_case, l_ver, l_alg)
    gd.generate_docx(file_save, "")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: tf_executable dir_in")
        exit(0)
    dir_test = str(os.fsdecode(sys.argv[1]))
    print("dir_input: {}".format(dir_test))
    deviation_report(dir_test)
