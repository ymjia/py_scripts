# -*- coding: utf-8 -*-
## @file generate_docx.py
## @brief create documents from given folder structure
## @author jiayanming

import os.path
import math

from docx import Document
from docx.shared import Inches
from docx.shared import Mm

dir_output = "d:/data/test_framwork/output/"

# input data read from config file
list_case = ["case1", "case2"]
# versions to be compared
list_ver = ["v11", "v12"]
# compare alg list
list_alg = ["smooth", "merge"]
# screen shot view list
cam_num = 3

col_num = len(list_ver)
document = Document()

# generate paraview project for given data
def get_paraview_project(dir_in, case, list_v, alg):
    # get source list
    list_dir = [os.path.join(dir_in, case, v) for v in list_v]
    list_annot = ["{}_{}_{}".format(case, v, alg) for v in list_v]
    # read file
    list_source = []
    list_view = []
    l_pos = []
    l = CreateLayout('Compare_{}'.format(s_num))
    # split layout and store positions
    pos = l.SplitHorizontal(0, 1 / len(list_view))
    l_pos = [pos, pos + 1]



def add_cell_content(cell, text, pic):
    pg = cell.paragraphs[0]
    run = pg.add_run()
    run.add_picture(pic, cell.width)
    cell.add_paragraph(text)


def add_case_table(doc, case):
    for alg in list_alg:
        table = document.add_table(rows=1, cols=col_num)
        row1 = table.rows[0]
        row1.cells[0].merge(row1.cells[col_num - 1])
        row1.cells[0].text = alg
        for cam in range(0, cam_num):
            row_cells = table.add_row().cells
            for vi in range(0, col_num):
                ver = list_ver[vi]
                dir_pic = os.path.join(dir_output, case, ver)
                name_pic = "ss_{}_v{}.png".format(alg, cam)
                file_pic = os.path.join(dir_pic, name_pic)
                add_cell_content(row_cells[vi], ver, file_pic)


document.add_heading("compare", 0)
for case in list_case:
    document.add_paragraph(
    case, style='List Bullet')
    add_case_table(document, case)

document.save("d:/tmp/compare.docx")
