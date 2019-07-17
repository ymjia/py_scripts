# -*- coding: utf-8 -*-
## @file ui_logic.py
## @brief ui signal/slot logitcs
## @author jiayanming

import os.path
import math
import sys
import datetime

import subprocess
from PyQt5.QtWidgets import QFileDialog, QMessageBox
sys.path.insert(0, r'c:/dev/py_scripts/')

from test_framework.project_io import get_checked_items
from test_framework.generate_docx import generate_docx


def slot_generate_docx(ui):
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    dir_doc = os.path.join(dir_o, "doc")
    doc_name = p_obj._docName
    str_time = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    p_obj._curDocName = "{}_{}.docx".format(doc_name, str_time)
    if not os.path.exists(dir_doc):
        os.makedirs(dir_doc)
    file_save = os.path.join(dir_doc, p_obj._curDocName)
    l_case = get_checked_items(p_obj._case, p_obj._dCaseCheck)
    l_ver = get_checked_items(p_obj._ver, p_obj._dVerCheck)
    l_alg = get_checked_items(p_obj._alg, p_obj._dAlgCheck)
    generate_docx(p_obj._configFile, dir_i, dir_o, file_save, l_case, l_ver, l_alg)
    QMessageBox.about(None, "Message", "Docx wrote to {}!".format(file_save))


def slot_open_docx(ui):
    p_obj = ui._p
    dir_doc = os.path.join(p_obj._dirOutput, "doc")
    file_doc = os.path.join(dir_doc, p_obj._curDocName)
    if os.path.exists(file_doc):
        os.startfile(file_doc)
    else:
        QMessageBox.about(None, "Error", "Document doesnot Exist! Try Generate Docx First.")


def slot_open_docx_path(ui):
    p_obj = ui._p
    dir_doc = os.path.join(p_obj._dirOutput, "doc")
    if not os.path.exists(dir_doc):
        os.makedirs(dir_doc)
    os.startfile(dir_doc)


def slot_create_screenshots(ui):
    p_obj = ui._p
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    l_case = get_checked_items(p_obj._case, p_obj._sCaseCheck)
    l_alg = get_checked_items(p_obj._alg, p_obj._sAlgCheck)
    l_ver = get_checked_items(p_obj._ver, p_obj._sVerCheck)
    # write to file
    filename = "c:/tmp/ss_config.txt"
    line_case = "cas"
    for c in l_case:
        line_case = line_case + " {}".format(c)
    line_ver = "ver"
    for c in l_ver:
        line_ver = line_ver + " {}".format(c)
    line_alg = "alg"
    for c in l_alg:
        line_alg = line_alg + " {}".format(c)
    f_config = open(filename, "w")
    f_config.writelines(line_case)
    f_config.writelines(line_ver)
    f_config.writelines(line_alg)
    f_config.close()
    # run pvpython.exe
    exe_pvpython = p_obj._exePV
    proc_ss = subprocess.Popen(
        [exe_pvpython,
         dir_i, dir_o, f_config])
    proc_ss.wait()


# get file and set qle.text
def slot_get_path(qle):
    path = QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QFileDialog.ShowDirsOnly)
    if path is not None and path != "":
        qle.setText(path)


def slot_get_file(qle, f_type):
    path = ""
    if f_type == "xml":
        path, _filter = QFileDialog.getOpenFileName(None, 'Open File', '', 'XML (*.xml)')
    else:
        path, _filter = QFileDialog.getOpenFileName(None, 'Open File', '', 'EXE (*.exe)')
    if path is not None and path != "":
        qle.setText(path)


def generate_exe_param(ui, case):
    param = ""
    return param


def slot_exe_run(ui):
    cur_obj = ui._p
    exe = cur_obj._exeDemo
    #list_case = ui.get_checked_items(cur_obj._case, cur_obj._
    param = generate_exe_param(ui)
    proc_demo = subprocess.Popen([exe, param])
    proc_demo.wait()
