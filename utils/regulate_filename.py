# -*- coding: UTF-8
## @file regulate_filename.py
## @brief 将文件夹中所有文件名中的字符‘-’/‘ ’统一为‘_’
## @usage (windows) py -3 regulate_filename.py DIR [REGEX]
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

# get regex
str_regex = ""
if len(sys.argv) == 3:
    str_regex = str(sys.argv[2])

file_rep_log = os.path.join(str_input, "filename_regulate_log.txt")
    
#get file
files = []
res_files = []
for file in os.listdir(dir_input):
    filename = os.fsdecode(file)
    file_split = os.path.splitext(filename)
    file_stem = file_split[0]
    mat_list = re.findall(str_regex, filename)
    if len(mat_list) < 1 : continue
    files.append(filename)


#start replace
#get max bit of numbers
open(file_rep_log, "w+").close();#clear file
fp_path = open(file_rep_log, "a+");
for i in range(0, len(files)):
    res_files.append(files[i].replace("-", "_"))
    res_files[i] = res_files[i].replace(" ", "_")
    fp_path.writelines("{} --> {}\n".format(files[i], res_files[i]))
    move(os.path.join(str_input, files[i]), os.path.join(str_input, res_files[i]))
