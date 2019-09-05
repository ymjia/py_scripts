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
from docx.oxml.ns import nsdecls
from docx.oxml import parse_xml
from docx.shared import Mm


## @brief read camera positions in input config
def read_cam(case_file):
    if not os.path.exists(case_file):
        return None
    content = None
    with open(case_file) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content if len(l) > 20]
    str_lines = [line.split(", ") for line in str_list]
    return [[float(s) for s in item] for item in str_lines if len(item) == 12]


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


def add_cell_content(cell, text, pic):
    if os.path.exists(pic):
        pg = cell.paragraphs[0]
        run = pg.add_run()
        run.add_picture(pic, cell.width)
    else:
        print("Warning: No ScreenShot {}".format(pic))
    cell.add_paragraph(text)


def shade_cell(cell):
    shading_ele = parse_xml(r'<w:shd {} w:fill="B8B8B8"/>'.format(nsdecls('w')))
    cell._tc.get_or_add_tcPr().append(shading_ele)


class DocxGenerator:
    def __init__(self, dir_input, dir_output, list_case, list_ver, list_alg):
        self._dirInput = dir_input
        self._dirOutput = dir_output
        self._listCase = list_case
        self._listVer = list_ver
        self._listAlg = list_alg
        self._doc = Document()

    # generate paraview project for given data
    def get_paraview_project(self, filename, case, alg):
        str_list_v = "["
        for v in self._listVer:
            str_list_v = str_list_v + "\"{}\",".format(v)
        str_list_v = str_list_v[:-1] + "]"
        file_content = """# -*- coding: utf-8 -*-\n## @brief Paraview Macro to reproduce data state\n## @author jiayanming_auto_generate\nimport os\nimport sys\ndir_py_module = os.path.join(os.getcwd(), \"..\", \"Sn3D_plugins\", \"scripts\", \"pv_module\")\nsys.path.append(dir_py_module)\nfrom framework_util import *\nload_state_files(r\"{}\", r\"{}\", \"{}\", \"{}\", {})\n""".format(self._dirInput, self._dirOutput, case, alg, str_list_v)
        with open(filename, "w") as text_file:
            text_file.write(file_content)

    def add_case_table(self, case, cam_num):
        col_num = len(self._listVer)
        for alg in self._listAlg:
            table = self._doc.add_table(rows=1, cols=col_num)
            table.style = 'Table Grid'
            row1 = table.rows[0]
            row1.cells[0].merge(row1.cells[col_num - 1])
            row1.cells[0].text = alg
            row2 = table.add_row().cells
            row2[0].merge(row2[col_num-1])
            name_state = "{}_{}_{}.py".format(case, alg, str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S")))
            dir_state = os.path.join(self._dirOutput, "ParaView_projects")
            if not os.path.exists(dir_state):
                os.makedirs(dir_state)
            file_state = os.path.join(dir_state, name_state)
            row2[0].text = file_state
            # color title
            shade_cell(row1.cells[0])
            shade_cell(row2[0])
            self.get_paraview_project(file_state, case, alg)
            for cam in range(0, cam_num):
                row_cells = table.add_row().cells
                for vi in range(0, col_num):
                    ver = self._listVer[vi]
                    dir_pic = os.path.join(self._dirOutput, case, ver)
                    name_pic = "ss_{}_v{}.png".format(alg, cam)
                    if ver == "input":
                        name_pic = "ss_input_v{}.png".format(cam)
                    file_pic = os.path.join(dir_pic, name_pic)
                    add_cell_content(row_cells[vi], ver, file_pic)
        return 0

    ## @brief generate docx file from given algorithm output dir, and config
    ## @param dir_input data case config directory
    ## @param dir_output algorithm/screenshots output directory
    ## @param file_config file contains user specified compare config
    def generate_docx(self, file_save, file_config):
        doc = self._doc
        # screen shot view list
        str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
        doc.add_heading("Compare Result {}".format(str_time), 0)
        doc.add_paragraph("From config file: {}".format(file_config))
        for case in self._listCase:
            doc.add_paragraph(case, style='List Bullet')
            list_cam = read_cam(os.path.join(self._dirInput, case, "config.txt"))
            if list_cam is None or len(list_cam) == 0:
                print("no cam table for {}".format(case))
                continue
            if self.add_case_table(case, len(list_cam)) != 0:
                print("Case Table Error for case: {}".format(case))
        doc.save(file_save)


def generate_docx_wrap(dir_input, dir_output, file_config):
    listCase, listVer, listAlg = read_compare_config(file_config)
    d = DocxGenerator(dir_input, dir_output, listCase, listVer, listAlg)
    # input data read from config file
    config_stem = os.path.splitext(os.path.split(file_config)[1])[0]
    str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    file_save = os.path.join(dir_output, "{}_{}.docx".format(config_stem, str_time))
    if len(sys.argv) == 2:
        file_save = str(sys.argv[1])
    d.generate_docx(file_save)


if __name__ == "__main__":
    dir_input = "d:/data/test_framwork/input/"
    dir_output = "d:/data/test_framwork/output/"
    file_config = "d:/data/test_framwork/compare.txt"
    generate_docx_wrap(dir_input, dir_output, file_config)
