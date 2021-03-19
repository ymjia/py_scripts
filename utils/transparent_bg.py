# -*- coding: UTF-8
## @file transparent_bg.py
## @brief make white tranparent
## @usage (windows) py -3 image_cut.py DIR x y w h [out_file_prefix]
## @author jiayanming01@shining3d.com

import sys

import os.path
from os.path import join
import re
import cv2


def process_pic(iname, oname):
    #load as color image BGR
    im_in = cv2.imread(iname)
    print(im_in.shape)
    im_bgra = cv2.cvtColor(im_in, cv2.COLOR_BGR2BGRA);
    h, w = im_bgra.shape[:2]
    for u in range(0, h):
        for v in range(0, w):
            pix = im_bgra[u][v]
            if pix[0] == 255 and pix[1] == 255 and pix[2] == 255:
                pix[3] = 0

    cv2.imwrite(oname, im_bgra)


#get input directory
str_input = sys.argv[1]
out_dir = os.path.join(str_input, "tb_out")
if not os.path.exists(out_dir):
    os.makedirs(out_dir)
for f in os.listdir(str_input):
    f_in = join(str_input, f)
    if os.path.isdir(f_in):
        continue
    process_pic(f_in, join(out_dir, f))
