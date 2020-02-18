# -*- coding: utf-8 -*-
## @file tex_check.py
## @brief get tex information from pdf 
## @author jiayanming

import os.path
import cv2
import numpy as np
import re
import math
import PIL
from PIL import Image
import openpyxl
from pdf2image import convert_from_path
import tesserocr
from tesserocr import PyTessBaseAPI
from operator import itemgetter


#constants

tmp_dir = "c:/tmp/img_out/"
in_dir = "c:/data/xls/check/"
pdf = os.path.join(in_dir, "SSHGMFP0620011610540.pdf")

table_num = [1, 2]

# variables
item_list = []


class tex_item:
    def __init__():
        self.date = ""
        self.no = ""
        self.idx = ""
        self.tex_type = ""
        self.port = ""
        self.amount = 0


def tuple_mean(tu4):
    return (int(tu4[0] + tu4[2] / 2), int(tu4[1] + tu4[3] / 2))


class ocr_table:
    def __init__(self, w, h):
        self._h = h
        self._w = w
        self._origin = (0, 0)
        self._pos = []
    
    def r(self, rid):
        start = rid * self._w
        return _pos[start:start + self._h]

    def rect(self, rid, cid):
        rn = rid + 1
        cn = rid + 1
        if rn >= self._h or cn >= self._w:
            return (0, 0, 0, 0)
        top_right = _pos[rid * self._w + cid]
        low_left = _pos[rn * self._w + cn]
        return (top_right[0] + origin[0], top_right[1] + origin[1],
                low_left[0] + origin[0], low_left[1] + origin[1])

def generate_table(origin, horizontal, vertical, joints):
    c_dots = cv2.findContours(joints, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
    c_h_lines = cv2.findContours(horizontal, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
    c_v_lines = cv2.findContours(vertical, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
    d_num = len(c_dots)
    h_num = len(c_h_lines)
    v_num = len(c_v_lines)
    t = ocr_table(v_num, h_num)
    t._origin = origin
    all_dots = []
    for d in c_dots:
        t._pos.append(tuple_mean(cv2.boundingRect(d)))
    # sort by row then col
    # ALTERNATIVE: calulate by v/h line coord 
    t._pos.sort(key = itemgetter(1))
    for li in range(0, h_num):
        start = li * v_num
        end = start + v_num
        sub_line = t._pos[start:end]
        t._pos[start:end] = sorted(sub_line, key = itemgetter(0))
    return t

def all_table_ocr(name):
    # load image
    src = cv2.imread(name)
    # size
    x = 0
    y = 0
    rsz = src[y:y+1000, x:x+1600]
    Image.fromarray(rsz).save(os.path.join(tmp_dir, "rsz.png"))
    # grey
    grey = cv2.cvtColor(rsz, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(cv2.bitwise_not(grey), 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, -2)
    Image.fromarray(bw).save(os.path.join(tmp_dir, "grey.png"))
    # extract horizontal
    horizontal = bw
    vertical = bw
    scale = 15 # min length to be detected threshold
    h, w = horizontal.shape[:2]
    # Specify size
    horizontalsize = int(w / scale)
    verticalsize = int(h / scale)
    # Create structure element for extracting lines through morphology operations
    h_pattern = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontalsize, 1))
    v_pattern = cv2.getStructuringElement(cv2.MORPH_RECT, (1, verticalsize))
    # Apply morphology operations
    horizontal = cv2.erode(horizontal, h_pattern, iterations = 1)
    horizontal = cv2.dilate(horizontal, h_pattern, iterations = 1)
    vertical = cv2.erode(vertical, v_pattern)
    vertical = cv2.dilate(vertical, v_pattern)
    Image.fromarray(horizontal).save(os.path.join(tmp_dir, "horizon.png"))
    Image.fromarray(vertical).save(os.path.join(tmp_dir, "vertical.png"))
    joints = cv2.bitwise_and(horizontal, vertical)
    Image.fromarray(joints).save(os.path.join(tmp_dir, "joints.png"))

    # divide and sort tables
    tables = cv2.bitwise_or(horizontal, vertical)
    c_tables = cv2.findContours(tables, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    all_tables = []
    for ct in c_tables:
        all_tables.append(cv2.boundingRect(ct))
    all_tables.sort(key=itemgetter(0,1))

    list_table = []
    for tb in all_tables:
        x = tb[0]
        y = tb[1]
        w = tb[2]
        h = tb[3]
        sub_h = horizontal[y:y+h, x:x+w]
        sub_v = vertical[y:y+h, x:x+w]
        sub_j = joints[y:y+h, x:x+w]
        list_table.append(generate_table((x, y), sub_h, sub_v, sub_j))

    return list_table


def my_decode(str_in):
    return str_in.encode('utf-8').decode("gbk", 'ignore')

def build_tex_item(img):
    res = tex_item
    #cv_img = cv2.imread(img_name)

    # ret, thresh = cv2.threshold(cv_img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # # choose 4 or 8 for connectivity type
    # connectivity = 4  
    # # Perform the operation
    # output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    # # Get the results
    # # The first cell is the number of labels
    # num_labels = output[0]
    # # The second cell is the label matrix
    # labels = output[1]
    # cv2.imshow('Original Image', labels)
    # # The third cell is the stat matrix
    # stats = output[2]
    # # The fourth cell is the centroid matrix
    # centroids = output[3]
    img_part1 = img.crop(area_idx)
    text = tesserocr.image_to_text(img_part1, lang="chi_sim+eng")
    img_part1.save(os.path.join(tmp_dir, "area1.png"))
    f = open(os.path.join(tmp_dir, "area1.txt"), "w", encoding='utf-8')
    f.writelines(text)  # print ocr text from image
    return res


def image_preprocess(img):
    gray = img.convert('L')
    blackwhite = gray.point(lambda x: 0 if x < 180 else 255, '1')
    return blackwhite
    #return img


def get_info_from_pdf(pdf):
    images = convert_from_path(pdf)
    idx = 0
    img_name2 = os.path.join(tmp_dir, "img_2.png")
    images[0].save(img_name2)
    all_table_ocr(img_name2)
    #build_tex_item(img_name2)
    
    #build_tex_item(images[1])
    return
    for img in images:
        # get info
        #build_tex_item
        img_p = image_preprocess(img)
        img_name = os.path.join(in_dir, "img_{}.png".format(idx))
        #img_p.save(img_name)
        build_tex_item(img_name)
        idx += 1
        break


def write_item_to_file(filename, out_list):
    wb = Workbook()
    ws = wb.active
    ws.append(["日期", "报关单号", "税单序号", "税种", "申报口岸", "税款金额"])
    for vi in out_list:
        ws.append([vi.date, vi.no, vi.idx, vi.tex_type, vi.port, vi.amount])
    wb.save(filename)


get_info_from_pdf(pdf)
