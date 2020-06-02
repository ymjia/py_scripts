# -*- coding: utf-8 -*-
## @file move_dll.py
## @brief move dll from txt file
## @usage (windows) py -3 move_dll.py input_file move_destination
## @author jiayanming01@shining3d.com

import sys
import os.path
from shutil import copy2

if len(sys.argv) < 3:
    print("Error: No input directory!")
    print("Usage: " + str(argv[0]) + "input_file move_destination")
    raise SystemExit

file_input = str(sys.argv[1])
dir_output = str(sys.argv[2])
print(file_input)
print(dir_output)
if not(os.path.exists(dir_output)):
    os.makedirs(dir_output)
f = open(file_input, "r")
for line in f:
    print(line)
    copy2(str(line).strip(), dir_output)
