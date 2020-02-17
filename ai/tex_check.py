# -*- coding: utf-8 -*-
## @file tex_check.py
## @brief get tex information from pdf 
## @author jiayanming

import os.path
import cv2
import re
import math
import PIL
from PIL import Image
from openpyxl import *
from pdf2image import convert_from_path
import tesserocr
from tesserocr import PyTessBaseAPI
pdf = "c:/data/xls/check/SSHGMFP0620011610540.pdf"


class tex_item:
    def __init__():
        self.date = ""
        self.no = ""
        self.idx = ""
        self.tex_type = ""
        self.port = ""
        self.amount = 0

area_no = (330, 185, 580, 230)
area_idx = (1010, 185, 1070, 230)
area_no = (330, 185, 580, 230)
area_no = (330, 185, 580, 230)
area_no = (330, 185, 580, 230)

item_list = []


def my_decode(str_in):
    return str_in.encode('utf-8').decode("gbk", 'ignore')

def build_tex_item(img_name):
    res = tex_item
    cv_img = cv2.imread(img_name)

    ret, thresh = cv2.threshold(cv_img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    # choose 4 or 8 for connectivity type
    connectivity = 4  
    # Perform the operation
    output = cv2.connectedComponentsWithStats(thresh, connectivity, cv2.CV_32S)
    # Get the results
    # The first cell is the number of labels
    num_labels = output[0]
    # The second cell is the label matrix
    labels = output[1]
    cv2.imshow('Original Image', labels)
    # The third cell is the stat matrix
    stats = output[2]
    # The fourth cell is the centroid matrix
    centroids = output[3]
    #img_part1 = img.crop(area_idx)
    # text = tesserocr.image_to_text(img_part1, lang="chi_sim+eng")
    # print(text.getBoxRects())
    # img_part1.save("c:/tmp/img_out/area1.png")
    # f = open("c:/tmp/img_out/area1.txt", "w", encoding='utf-8')
    # f.writelines(text)  # print ocr text from image
    return res


def image_preprocess(img):
    gray = img.convert('L')
    blackwhite = gray.point(lambda x: 0 if x < 180 else 255, '1')
    return blackwhite
    #return img


def get_info_from_pdf(pdf):
    images = convert_from_path(pdf)
    idx = 0
    img_name2 = "c:/data/xls/check/img_2.png"
    images[1].save(img_name2)
    build_tex_item(img_name2)
    return
    for img in images:
        # get info
        #build_tex_item
        img_p = image_preprocess(img)
        img_name = "c:/data/xls/check/img_{}.png".format(idx)
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
