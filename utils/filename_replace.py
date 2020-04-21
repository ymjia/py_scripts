# -*- coding: UTF-8
## @file filename_replace.py
## @brief 替换文件夹中的文件名字符串
## @usage (windows) py -3 filename_replace.py DIR REGEX_in str_replace
## @author jiayanming01@shining3d.com

import sys
import os.path
import re
from shutil import move

# command parameters
if len(sys.argv) != 4:
    print("Error: No input directory!")
    print("Usage: " + str(argv[0]) + " file_dir regex replace_str")
    raise SystemExit

#get input directory
str_input = sys.argv[1]
dir_input = os.fsencode(str_input)
if not(os.path.exists(dir_input)):
    print("Input Directory {} does not Exists!".format(dir_input))
    raise SystemExit

# get regex
str_regex = str(sys.argv[2])
str_replace = str(sys.argv[3])

# log change
file_rep_log = os.path.join(str_input, "filename_replace_log.txt")
open(file_rep_log, "w+").close();#clear file
fp_path = open(file_rep_log, "a+");

# replace
for file in os.listdir(dir_input):
    filename = os.fsdecode(file)
    f_new = re.sub(str_regex, str_replace, filename)
    if filename == f_new: continue
    fp_path.writelines("{} --> {}\n".format(filename, f_new))
    move(os.path.join(str_input, filename), os.path.join(str_input, f_new))



    
