# -*- coding: utf-8 -*-
## @file generate_docx.py
## @brief create documents from given folder structure
## @author jiayanming

import os.path
import math

from docx import Document
from docx.shared import Inches
from docx.shared import Mm

dir_output = "c:/data/test_framwork/output/"

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

def genearte_view(s_num):
    l = CreateLayout('Compare_{}'.format(s_num))
    # view positions in layout
    l_pos = []

    # split layout and store positions
    if s_num == 2:
        pos = l.SplitHorizontal(0, 0.5)
        l_pos = [pos, pos + 1]

    # 3 view horizontally
    if s_num == 3:
        pos = l.SplitHorizontal(0, 0.33)
        pos2 = l.SplitHorizontal(pos + 1, 0.5)
        l_pos = [pos, pos2, pos2 + 1]

    # 2 X 2
    if s_num == 4:
        tmp = l.SplitHorizontal(0, 0.5)
        pos0 = l.SplitVertical(tmp, 0.5)
        pos1 = l.SplitVertical(tmp + 1, 0.5)
        l_pos = [pos0, pos0 + 1, pos1, pos1 + 1]

    # 2 X 2 + 1 / 3 X 2
    if s_num == 5 or s_num == 6:
        # split horizontally to 3
        tmp1 = l.SplitHorizontal(0, 0.33)
        tmp2 = l.SplitHorizontal(tmp1 + 1, 0.5)
        tmp3 = tmp2 + 1
        pos0 = l.SplitVertical(tmp1, 0.5)
        pos1 = l.SplitVertical(tmp2, 0.5)
        pos2 = tmp3
        if s_num == 6:
            # split last one
            pos2 = l.SplitVertical(tmp3, 0.5)
        l_pos = [pos0, pos0 + 1, pos1, pos1 + 1, pos2]
        if s_num == 6:
            l_pos.append(pos2 + 1)
    return l_pos

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

document.save("c:/tmp/compare.docx")
