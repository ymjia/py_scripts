# -*- coding: UTF-8
## @file undo_regulate_filename.py
## @brief 撤消regulate_filename_number.py对文件名的修改
## @usage (windows) py -3 regulate_filename_number.py DIR [REGEX]
## @author jiayanming01@shining3d.com

import sys
import os.path
import re
from shutil import move

# command parameters
if len(sys.argv) < 2:
    print("Error: No input directory!")
    print("Usage: " + str(argv[0]) + " testbug_input_dir" + "[match regex]")
    raise SystemExit


#get input directory
str_input = sys.argv[1]
dir_input = os.fsencode(str_input)
if not(os.path.exists(dir_input)):
    print("Input Directory {} does not Exists!".format(dir_input))
    raise SystemExit

file_log = os.path.join(str_input, "filename_replace_log.txt")
# get regex
str_regex = ""
if len(sys.argv) == 3:
    str_regex = str(sys.argv[2])

file_rep_log = os.path.join(str_input, "filename_replace_log.txt")

if not(os.path.exists(file_rep_log)):
    print("Input Directory {} does not have name change log file!".format(dir_input))
    raise SystemExit

f = open(file_rep_log, "r")
for line in f:
    idx = line.find(" --> ")
    file_org = os.path.join(str_input, line[:idx])
    file_cur = os.path.join(str_input, line[idx + 5:-1])
    if not os.path.exists(file_cur): continue
    move(os.path.join(str_input, file_cur), os.path.join(str_input, file_org))


