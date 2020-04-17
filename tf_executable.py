# -*- coding: utf-8 -*-
## @file tf_executable.py
## @brief test framework standalone executable
## @author jiayanming

import sys
import os
import datetime
from pathlib import Path
from shutil import move, rmtree
sys.path.insert(0, os.getcwd())
from test_framework.generate_docx import DocxGenerator
from test_framework.utils import SessionConfig
from test_framework.utils import g_config
from test_framework import create_screenshots


def deviation_report(f_a, f_b):
    if not os.path.exists(f_a) or not os.path.exists(f_b):
        print("Error! Input File does not Exists")
        return
    pa = Path(f_a)
    pb = Path(f_b)
    org_dir = str(pa.parent)
    dirve_dir = pa.drive + pa.root
    str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))    
    tmp_dir = os.path.join(dirve_dir, "hd_tmp_{}".format(str_time))
    case_name = "input"
    case_dir = os.path.join(tmp_dir, case_name)
    if not os.path.exists(case_dir):
        os.makedirs(case_dir)
    if not os.path.exists(case_dir):
        print("Error! Fail to create working dir {}".format(case_dir))
    sc = SessionConfig()
    sc.list_case = ["input"]
    sc.list_ver = ['__hausdorff']
    sc.list_alg = []
    print(sc.list_case)
    dir_in = tmp_dir
    dir_out = os.path.join(dir_in, "__output")
    if not os.path.exists(dir_out):
        os.makedirs(dir_out)

    sc.dir_i = dir_in
    sc.dir_o = dir_out

    # move files
    sc.config_map["{}_test_name".format(case_name)] = f_a
    sc.config_map["{}_ref_name".format(case_name)] = f_b
    f_tmp_a = os.path.join(case_dir, "a{}".format(pa.suffix))
    f_tmp_b = os.path.join(case_dir, "b{}".format(pb.suffix))
    move(f_a, f_tmp_a)
    move(f_b, f_tmp_b)
    total_num = create_screenshots.create_hausdorff_shot(sc)
    move(f_tmp_a, f_a)
    move(f_tmp_b, f_b)

    # generate docx
    doc_name_final = "Deviation_report_{}.docx".format(str_time)
    file_save = os.path.join(org_dir, doc_name_final)
    l_ver = ["hausdorff_A2B"]
    l_alg = ["__hd"] # reserved alg_name for hausdorff dist
    gd = DocxGenerator(dir_in, dir_out, sc.list_case, l_ver, l_alg)
    gd.generate_docx(file_save, "")
    rmtree(tmp_dir)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: tf_executable mesh_test mesh_ref [out_dir]")
        exit(0)
    fa = str(os.fsdecode(sys.argv[1]))
    fb = str(os.fsdecode(sys.argv[2]))
    deviation_report(fa, fb)
