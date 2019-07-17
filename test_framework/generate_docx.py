# -*- coding: utf-8 -*-
## @file generate_docx.py
## @brief create documents from given folder structure
## @note generated py file meed pv module/framework_util to be parsed
## @author jiayanming

import os.path
import math
import sys
import datetime
from docx import Document
from docx.shared import Inches
from docx.shared import Mm

## @brief read camera positions in input config
def read_cam(case_file):
    if not os.path.exists(case_file):
        return None
    content = None
    with open(case_file) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content]
    str_lines = [line.split(", ") for line in str_list]
    return [[float(s) for s in item] for item in str_lines]


## @brief read user concerned case name list
def read_config_list(config_str, pattern):
    lc = len(config_str)
    lp = len(pattern)
    if lc < lp:
        return None
    if config_str[0:lp] != pattern:
        return None
    return config_str[lp+1:].split(" ")


## @brief read all configs from config file
## @return tuple of config list
def read_compare_config(file_config):
    if not os.path.exists(file_config):
        return None
    case_list = []
    ver_list = []
    alg_list = []
    content = None
    with open(file_config) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content]
    for line in str_list:
        if line[0:3] == "cas":
            case_list = read_config_list(line, "cas")
        elif line[0:3] == "ver":
            ver_list = read_config_list(line, "ver")
        elif line[0:3] == "alg":
            alg_list = read_config_list(line, "alg")
    return case_list, ver_list, alg_list


# generate paraview project for given data
def get_paraview_project(filename, dir_in, case, alg, list_v):
    str_list_v = "["
    for v in list_v:
        str_list_v = str_list_v + "\"{}\",".format(v)
    str_list_v = str_list_v[:-1] + "]"
    file_content = """# -*- coding: utf-8 -*-\n## @brief Paraview Macro to reproduce data state\n## @author jiayanming_auto_generate\nimport os\nimport sys\ndir_py_module = os.path.join(os.getcwd(), \"..\", \"Sn3D_plugins\", \"scripts\", \"pv_module\")\nsys.path.append(dir_py_module)\nfrom framework_util import *\nload_state_files(\"{}\", \"{}\", \"{}\", {})\n""".format(dir_in, case, alg, str_list_v)
    with open(filename, "w") as text_file:
        text_file.write(file_content)

def add_cell_content(cell, text, pic):
    pg = cell.paragraphs[0]
    run = pg.add_run()
    run.add_picture(pic, cell.width)
    cell.add_paragraph(text)


def add_case_table(doc, dir_in, case, list_ver, list_alg, cam_num):
    col_num = len(list_ver)
    for alg in list_alg:
        table = doc.add_table(rows=1, cols=col_num)
        table.style = 'Table Grid'
        row1 = table.rows[0]
        row1.cells[0].merge(row1.cells[col_num - 1])
        row1.cells[0].text = alg
        row2 = table.add_row().cells
        row2[0].merge(row2[col_num-1])
        name_state = "{}_{}_{}.py".format(case, alg, str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
        dir_state = os.path.join(dir_in, "ParaView_projects")
        if not os.path.exists(dir_state):
            os.makedirs(dir_state)
        file_state = os.path.join(dir_state, name_state)
        row2[0].text = file_state
        get_paraview_project(file_state, dir_in, case, alg, list_ver)
        for cam in range(0, cam_num):
            row_cells = table.add_row().cells
            for vi in range(0, col_num):
                ver = list_ver[vi]
                dir_pic = os.path.join(dir_in, case, ver)
                name_pic = "ss_{}_v{}.png".format(alg, cam)
                file_pic = os.path.join(dir_pic, name_pic)
                add_cell_content(row_cells[vi], ver, file_pic)


## @brief generate docx file from given algorithm output dir, and config
## @param dir_input data case config directory
## @param dir_output algorithm/screenshots output directory
## @param file_config file contains user specified compare config
def generate_docx(file_config, dir_input, dir_output, file_save, list_case, list_ver, list_alg):
    # screen shot view list
    str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    document = Document()
    document.add_heading("Compare Result {}".format(str_time), 0)
    document.add_paragraph("From config file: {}".format(file_config))
    for case in list_case:
        document.add_paragraph(case, style='List Bullet')
        list_cam = read_cam(os.path.join(dir_input, case, "config.txt"))
        add_case_table(document, dir_output, case, list_ver, list_alg, len(list_cam))
    document.save(file_save)


def generate_docx_wrap(dir_input, dir_output, file_config):
    # input data read from config file
    list_case, list_ver, list_alg = read_compare_config(file_config)
    config_stem = os.path.splitext(os.path.split(file_config)[1])[0]
    str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    file_save = os.path.join(dir_output, "{}_{}.docx".format(config_stem, str_time))
    if len(sys.argv) == 2:
        file_save = str(sys.argv[1])
    generate_docx(file_config, dir_input, dir_output, file_save, list_case, list_ver, list_alg)


if __name__ == "__main__":
    dir_input = "d:/data/test_framwork/input/"
    dir_output = "d:/data/test_framwork/output/"
    file_config = "d:/data/test_framwork/compare.txt"
    generate_docx_wrap(dir_input, dir_output, file_config)
