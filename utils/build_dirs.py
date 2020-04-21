# -*- coding: UTF-8
## @file build_dirs.py
## @brief 将对文件夹中所有文件创建同名子文件夹并移动
## @usage (windows) py -3 build_dirs.py DIR [REGEX]
## @author jiayanming01@shining3d.com

import sys
import os.path
import re
from shutil import move

# command parameters
if len(sys.argv) < 2:
    print("Error: No input directory!")
    print("Usage: " + str(argv[0]) + " file_dir [regex]")
    raise SystemExit

#get input directory
str_input = sys.argv[1]
dir_input = os.fsencode(str_input)
if not(os.path.exists(dir_input)):
    print("Input Directory {} does not Exists!".format(dir_input))
    raise SystemExit

# get regex
str_regex = ""
if len(sys.argv) > 2:
    str(sys.argv[2])


# replace
for file in os.listdir(dir_input):
    filename = os.fsdecode(file)
    if os.path.isdir(os.path.join(str_input, filename)):
        continue
    if str_regex != "" and re.search(str_regex, filename) is None:
        continue
    file_dir = os.path.splitext(filename)[0]
    if file_dir == filename:
        file_dir = "{}_d".format(filename)
    target_dir = os.path.join(str_input, file_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    if not os.path.exists(target_dir):
        print("Fail to create dir {}".format(target_dir))
        continue
    move(os.path.join(str_input, filename), os.path.join(target_dir, filename))
