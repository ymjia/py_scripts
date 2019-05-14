# -*- coding: utf-8 -*-
## @file generate_docx.py
## @brief create documents from given folder structure
## @author jiayanming

import os.path
import math

from docx import Document
from docx.shared import Inches
from docx.shared import Mm

# input data
list_case = ["case1", "case2"]
# versions to be compared
list_ver = ["input", "v1.1", "v1.2"]
# compare alg list
list_alg = ["rm_bd", "mereg"]
# screen shot view list
list_view = [1, 2, 3]

col_num = len(list_ver)
document = Document()

document.add_heading("compare", 0)

def add_cell_content(cell, text, pic):
    pg = cell.paragraphs[0]
    run = pg.add_run()
    run.add_picture(pic, cell.width)
    cell.add_paragraph(text)


def add_case_table(doc, case):
    for ai in range(0, len(list_alg)):
        table = document.add_table(rows=1, cols=col_num)
        row1 = table.rows[0]
        row1.cells[0].merge(row1.cells[col_num - 1])
        row1.cells[0].text = list_alg[ai]
        for view in list_view: 
            row_cells = table.add_row().cells
            for vi in range(0, col_num):
                cur_ver = list_ver[vi]
                #row_cells[vi].text = list_ver[vi]
                add_cell_content(row_cells[vi], list_ver[vi], "c:/data/new_reconstruction/1.jpg")

for case in list_case:
    document.add_paragraph(
    case, style='List Bullet')
    add_case_table(document, case)
    
document.save("c:/tmp/compare.docx")

