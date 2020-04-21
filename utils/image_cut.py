# -*- coding: UTF-8
## @file image_cut.py
## @brief ÇÐ¸îÍ¼Æ¬ÇøÓò
## @usage (windows) py -3 image_cut.py DIR x y w h [out_file_prefix]
## @author jiayanming01@shining3d.com

import sys

import os.path
import re
import cv2

# command parameters
if len(sys.argv) < 6:
    print("Error: No input directory!")
    print("Usage: " + str(argv[0]) + " DIR x y w h [out_file_prefix]")
    raise SystemExit

#get input directory
str_input = sys.argv[1]
dir_input = os.fsencode(str_input)
if not(os.path.exists(dir_input)):
    print("Input Directory {} does not Exists!".format(dir_input))
    raise SystemExit

out_prefix = "clip"
if len(sys.argv) > 6:
    out_prefix = str(sys.argv[6])

x = int(sys.argv[2])
y = int(sys.argv[3])
w = int(sys.argv[4])
h = int(sys.argv[5])

out_dir = os.path.join(str_input, "clip")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
if os.path.exists(out_dir):
    for file in os.listdir(dir_input):
        filename = os.fsdecode(file)
        if not os.path.isfile(os.path.join(str_input, filename)):
            continue
        f_stem, f_ext = os.path.splitext(filename)
        file_out = "{}_{}.png".format(f_stem, out_prefix)
        img = cv2.imread(os.path.join(str_input, filename))
        if img is None:
            print("can not read image file: {}".format(filename))
            continue
        crop_img = img[y:y+h, x:x+w]
        cv2.imwrite(os.path.join(out_dir, file_out), crop_img)
