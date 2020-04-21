# -*- coding: utf-8 -*-
## @file regulate_filename.py
## @brief 将路径中的数据名标准化，用于tf的输入
## @usage (windows) py -3 regulate_tf_input_files.py DIR
## @author jiayanming01@shining3d.com

import sys
import os.path
import re
from shutil import move

# command parameters
if len(sys.argv) < 2:
    print("Error: No input directory!")
    print("Usage: " + str(argv[0]) + " input_dir")
    raise SystemExit

chinese = ["成品基台", "代型", "扫描杆", "未分模", "印模"]
replace = ["ABUTMENT", "DIE", "POD", "UNSEP", "IMPRESS"]


#get input directory
str_input = sys.argv[1]
dir_input = os.fsencode(str_input)
if not(os.path.exists(dir_input)):
    print("Input Directory {} does not Exists!".format(dir_input))
    raise SystemExit





def move_stero_build_result(root):
    sbr = os.path.join(root, "StereoBuildResult")
    if not os.path.exists(sbr):
        return
    org_info = os.path.join(root, "org_info")
    if not os.path.exists(org_info):
        os.makedirs(org_info)
    if not os.path.exists(org_info):
        print("Error cannot create dir: {}".format(org_info))
        return
    # move all file in org_info
    for f in os.listdir(root):
        f_str = os.fsdecode(f)
        if f == "StereoBuildResult" or f == "org_info":
            continue
        move(os.path.join(root, f_str), os.path.join(org_info, f_str))
        #print("{} --{}".format(os.path.join(root, f_str), os.path.join(org_info, f_str)))
    # move out files in sterobuildresult
    for f in os.listdir(sbr):
        move(os.path.join(sbr, f), root)
        #print("{} ----{}".format(os.path.join(sbr, f), root))


def regulate_flow_name(root_b):
    root = os.fsdecode(root_b)
    for d in os.listdir(root):
        if os.path.isfile(d):
            continue
        dir_str = os.fsdecode(d)
        try:
            pos = chinese.index(dir_str)
        except:
            continue
        os.rename(os.path.join(root, dir_str), os.path.join(root, replace[pos]))
        #print("{} \n {}".format(os.path.join(root, dir_str), os.path.join(root, replace[pos])))
        sub_root = os.path.join(root, replace[pos])
        for case in os.listdir(sub_root):
            if os.path.isfile(case):
                continue
            move_stero_build_result(os.path.join(sub_root, case))

for scanner in os.listdir(dir_input):
    if os.path.isfile(scanner):
        continue
    regulate_flow_name(os.path.join(dir_input, scanner))
