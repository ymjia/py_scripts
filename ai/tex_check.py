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
import docx
from pdf2image import convert_from_path
import tesserocr
from tesserocr import PyTessBaseAPI
from operator import itemgetter


#constants
tmp_dir = "c:/tmp/img_out/"
in_dir = "c:/data/xls/check/"
pdf = os.path.join(in_dir, "SSHGMFP0620011610540.pdf")

## @brief tex info item from pdf
class tex_item:
    def __init__(self):
        self.date = ""
        self.no = ""
        self.idx = ""
        self.tex_type = ""
        self.port = ""
        self.amount = 0
        self.img_date = None
        self.img_no = None
        self.img_idx = None
        self.img_tex_type = None
        self.img_port = None
        self.img_amount = None


## @brief ocr table info (cell pixel positions) from image
class ocr_table:
    def __init__(self, w, h):
        self._h = h # height
        self._w = w # width
        self._origin = (0, 0) # table l-t-coner in image
        self._pos = [] # l-t-coner of each cell
    
    def r(self, rid):
        start = rid * self._w
        return self._pos[start:start + self._h]

    def rect(self, rid, cid):
        rn = rid + 1
        cn = cid + 1
        if rn >= self._h or cn >= self._w:
            return (0, 0, 0, 0)
        top_right = self._pos[rid * self._w + cid]
        low_left = self._pos[rn * self._w + cn]
        return (top_right[0] + self._origin[0], top_right[1] + self._origin[1],
                low_left[0] + self._origin[0], low_left[1] + self._origin[1])

    def lrect(self, rid, cid):
        rn = rid + 1
        cn = cid + 1
        if rn >= self._h or cn >= self._w:
            return (0, 0, 0, 0)
        top_right = self._pos[rid * self._w + cid]
        low_left = self._pos[rn * self._w + cn]
        return (top_right[0], top_right[1], low_left[0], low_left[1])


## @brief get mean poisition from cv coutour boundingRect
def tuple_mean(tu4):
    return (int(tu4[0] + tu4[2] / 2), int(tu4[1] + tu4[3] / 2))


## @brief generate table information from ocr region
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


## @brief detect tables from image file
def ocr_detect_table(name):
    # load image
    src = cv2.imread(name)
    # size
    x = 0
    y = 0
    rsz = src[y:y+1000, x:x+1600]
    #Image.fromarray(rsz).save(os.path.join(tmp_dir, "rsz.png"))
    # grey
    grey = cv2.cvtColor(rsz, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(cv2.bitwise_not(grey), 255,
                               cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, -2)
    #Image.fromarray(bw).save(os.path.join(tmp_dir, "grey.png"))
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
    #Image.fromarray(horizontal).save(os.path.join(tmp_dir, "horizon.png"))
    #Image.fromarray(vertical).save(os.path.join(tmp_dir, "vertical.png"))
    joints = cv2.bitwise_and(horizontal, vertical)
    #Image.fromarray(joints).save(os.path.join(tmp_dir, "joints.png"))

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


def rect_shrink(rect, step):
    res = (rect[0] + step, rect[1] + step,
           rect[2] - step, rect[3] - step)
    return res

## @brief recognize text from regions defined by ocr_table
def build_tex_item(org, tables):
    res = tex_item()
    img = image_preprocess(org)
    to = tables[0]._origin
    date_rect = (to[0]-240, to[1] - 105, to[0] + 20, to[1] - 60)
    res.img_date = img.crop(date_rect)
    res.img_no = img.crop(rect_shrink(tables[0].rect(0, 0), 3))
    res.img_idx = img.crop(rect_shrink(tables[1].rect(0, 0), 3))
    res.img_tex_type = img.crop(rect_shrink(tables[0].rect(1, 0), 3))
    res.img_port = img.crop(rect_shrink(tables[0].rect(2, 0), 3))
    res.img_amount = img.crop(rect_shrink(tables[0].rect(9, 0), 3))
    
    res.date = tesserocr.image_to_text(res.img_date, lang="chi_sim+eng")
    res.no = tesserocr.image_to_text(res.img_no, lang="chi_sim+eng")
    res.idx = tesserocr.image_to_text(res.img_idx, lang="chi_sim+eng")
    res.tex_type = tesserocr.image_to_text(res.img_tex_type, lang="chi_sim+eng")
    res.port = tesserocr.image_to_text(res.img_port, lang="chi_sim+eng")
    try:
        res.amount = float(tesserocr.image_to_text(res.img_amount, lang="chi_sim+eng"))
    except:
        res.amount = 0
    return res


def image_preprocess(img):
    gray = img.convert('L')
    blackwhite = gray.point(lambda x: 0 if x < 200 else 255, '1')
    return blackwhite


def get_info_from_pdf(pdf, info_list):
    item_list.clear()
    images = convert_from_path(pdf)
    for idx, img in enumerate(images):
        img_name = os.path.join(tmp_dir, "img_{}.png".format(idx))
        img.save(img_name)
        tables = ocr_detect_table(img_name)
        if len(tables) != 2:
            print("Error! Fail to detect table from pdf {}".format(img_name))
            continue
        item_list.append(build_tex_item(img, tables))


def write_item_to_xls(filename, out_list):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["日期", "报关单号", "税单序号", "税种", "申报口岸", "税款金额"])
    for vi in out_list:
        ws.append([vi.date, vi.no, vi.idx, vi.tex_type, vi.port, vi.amount])
    wb.save(filename)


def doc_add_cell_pic(cell, pic):
    img_name = os.path.join(tmp_dir, "img_{}.png".format(5))
    pic.save(img_name)
    if os.path.exists(img_name):
        pg = cell.paragraphs[0]
        run = pg.add_run()
        run.add_picture(img_name, cell.width)


def write_item_to_doc(filename, out_list):
    doc = docx.Document()
    i_num = len(out_list)
    table = doc.add_table(rows=1, cols=6)
    table.style = 'Table Grid'
    row1 = table.rows[0]
    row1.cells[0].text = "日期"
    row1.cells[1].text = "报关单号"
    row1.cells[2].text = "税单序号"
    row1.cells[3].text = "税种"
    row1.cells[4].text = "申报口岸"
    row1.cells[5].text = "税款金额"
    for idx, item in enumerate(out_list):
        txt_cells = table.add_row().cells
        txt_cells[0].text = item.date
        txt_cells[1].text = item.no
        txt_cells[2].text = item.idx
        txt_cells[3].text = item.tex_type
        txt_cells[4].text = item.port
        txt_cells[5].text = str(item.amount)
        pic_cells = table.add_row().cells
        doc_add_cell_pic(pic_cells[0], item.img_date)
        doc_add_cell_pic(pic_cells[1], item.img_no)
        doc_add_cell_pic(pic_cells[2], item.img_idx)
        doc_add_cell_pic(pic_cells[3], item.img_tex_type)
        doc_add_cell_pic(pic_cells[4], item.img_port)
        doc_add_cell_pic(pic_cells[5], item.img_amount)
    doc.save(filename)


item_list = []
get_info_from_pdf(pdf, item_list)
write_item_to_xls(os.path.join(tmp_dir, "res.xlsx"), item_list)
write_item_to_doc(os.path.join(tmp_dir, "res.docx"), item_list)
