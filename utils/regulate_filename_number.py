# -*- coding: UTF-8
## @file regulate_filename_number.py
## @brief 将文件夹中所有带数字的文件名中的数字补0对齐
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

# get regex
str_regex = ""
if len(sys.argv) == 3:
    str_regex = str(sys.argv[2])

file_rep_log = os.path.join(str_input, "filename_replace_log.txt")
    
#get file
files = []
res_files = []
max_num = 0
num_list = []
for file in os.listdir(dir_input):
    if not os.path.isfile(os.path.join(dir_input, file)): continue
    filename = os.fsdecode(file)
    file_split = os.path.splitext(filename)
    file_stem = file_split[0]
    mat_list = re.findall(str_regex, filename)
    if len(mat_list) < 1 : continue
    mat_list = re.findall("[0-9]+", file_stem)
    mat_num = len(mat_list)
    if mat_num == 0: continue
    #find matched files
    cur_num = mat_list[mat_num - 1]
    max_num = max(max_num, int(cur_num))
    files.append(filename)
    num_list.append(cur_num)

#start replace
#get max bit of numbers
bit_num = len(str(max_num))
open(file_rep_log, "w+").close();#clear file
fp_path = open(file_rep_log, "a+");
for i in range(0, len(files)):
    reg_find = "(.*){}".format(num_list[i])
    reg_replace = "\\g<1>{:0{}}".format(int(num_list[i]), bit_num)
    res_files.append(re.sub(reg_find, reg_replace, files[i]))
    fp_path.writelines("{} --> {}\n".format(files[i], res_files[i]))
    move(os.path.join(str_input, files[i]), os.path.join(str_input, res_files[i]))



    
