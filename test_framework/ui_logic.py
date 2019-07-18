# -*- coding: utf-8 -*-
## @file ui_logic.py
## @brief ui signal/slot logitcs
## @author jiayanming

import os.path
import sys
import datetime
import subprocess

from PyQt5.QtWidgets import QFileDialog, QMessageBox
dir_parent = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.dirname(dir_parent))
from test_framework import project_io
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
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    l_case = get_checked_items(p_obj._case, p_obj._sCaseCheck)
    l_alg = get_checked_items(p_obj._alg, p_obj._sAlgCheck)
    l_ver = get_checked_items(p_obj._ver, p_obj._sVerCheck)
    # write to file
    filename = os.path.join(dir_o, "ss_config.txt")
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
    f_config.write(line_case + "\n")
    f_config.write(line_ver + "\n")
    f_config.write(line_alg + "\n")
    f_config.close()
    # run pvpython.exe
    exe_pvpython = p_obj._exePV
    dir_pv_wd = os.path.dirname(exe_pvpython)
    py_ss = os.path.join(os.path.dirname(os.path.realpath(__file__)), "create_screenshots.py")
    proc_ss = subprocess.Popen(
        [exe_pvpython, py_ss,
         dir_i, dir_o, filename], cwd=dir_pv_wd)
    proc_ss.wait()
    QMessageBox.about(None, "Message", "Create Screenshots Completed!")

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
    p_obj = ui._p
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    ver = p_obj._eVer
    p_i = os.path.join(dir_i, case)
    p_o = os.path.join(dir_o, case, ver)
    param = p_obj._exeParam
    return param.replace("{i}", p_i).replace("{o}", p_o)


def slot_exe_run(ui):
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    exe = p_obj._exeDemo
    list_case = get_checked_items(p_obj._case, p_obj._eCaseCheck)
    for case in list_case:
        param = generate_exe_param(ui, case)
        QMessageBox.about(None, "Message", param)
        continue
        proc_demo = subprocess.Popen([exe, param])
        proc_demo.wait()


def slot_new_project(ui):
    p = project_io.Project()
    ui.fill_ui_info(p)
    return


def slot_copy_project(ui):
    return


def slot_save_project(ui):
    # update project object
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    # update xml object
    p_obj._tree = p_obj.collect_xml()
    # save xml
    p_obj.save_xml()


def slot_load_project(ui):
    path, _filter = QFileDialog.getOpenFileName(None, 'Open File', '', 'XML (*.xml)')
    if not os.path.exists(path):
        QMessageBox.about(None, "Error", "Wrong file: {}!".format(path))
        return
    p = project_io.Project()
    p.load_xml(path)
    ui.fill_ui_info(p)
    return
