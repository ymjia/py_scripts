# -*- coding: utf-8 -*-
## @file ui_logic.py
## @brief ui signal/slot logitcs
## @author jiayanming

import os.path
import sys
import datetime
import subprocess
import xml.etree.ElementTree as ET

from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QInputDialog, QLineEdit,
                             QListView)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QItemSelection, QItemSelectionModel, QModelIndex

dir_parent = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.dirname(dir_parent))
from test_framework import project_io
from test_framework.project_io import get_checked_items
from test_framework import generate_docx


def ptree_add_item(pt, path):
    stem = os.path.splitext(os.path.basename(path))[0]
    root = pt.getroot()
    for item in root:
        if item.attrib["name"] == stem:
            return item
    new_item = ET.Element("", {"name": stem, "path": path})
    root.append(new_item)
    return new_item


def get_qlist_idx(qlv, name):
    model = qlv.model()
    for index in range(model.rowCount()):
        if model.item(index).text() == name:
            return index
    return -1


def set_project_selected(qlv, name):
    row = get_qlist_idx(qlv, name)
    if row < 0:
        return
    q_idx = qlv.model().index(row, 0)
    qlv.selectionModel().select(q_idx, QItemSelectionModel.Select)


def find_ptree_item(pt, name):
    root = pt.getroot()
    for item in root:
        if item.attrib["name"] == name:
            return item
    return None


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
    gd = generate_docx.DocxGenerator(dir_i, dir_o, l_case, l_ver, l_alg)
    gd.generate_docx(file_save, p_obj._configFile)
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
    path = QFileDialog.getExistingDirectory(None, 'Select a folder:', '', QFileDialog.ShowDirsOnly)
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


def slot_open_input_path(ui):
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    dir_in = QFileDialog.getExistingDirectory(None, 'Select a folder:', '', QFileDialog.ShowDirsOnly)
    if dir_in is None or dir_in == "":
        return
    p_obj._dirInput = dir_in
    p_obj._case = [f for f in os.listdir(dir_in)
                   if os.path.isdir(os.path.join(dir_in, f))]
    p_obj._eCaseCheck.clear()
    p_obj._sCaseCheck.clear()
    p_obj._dCaseCheck.clear()
    ui.fill_ui_info(p_obj)


support_ext = [".asc", ".rge", ".obj", ".stl", ".ply", ".srge", ".bin"]


def get_file_list(folder):
    res = []
    for name in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, name)):
            continue
        ext = os.path.splitext(name)[1]
        if not any(ext in e for e in support_ext):
            continue
        res.append(os.path.join(folder, name))
    return res


def generate_exe_param(ui, case):
    p_obj = ui._p
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    ver = p_obj._eVer
    p_i = os.path.join(dir_i, case) + "/"
    # use file name if only on file in case dir
    i_list = get_file_list(p_i)
    if len(i_list) == 1:
        p_i = i_list[0]
    # get output param
    p_o = os.path.join(dir_o, case, ver) + "/"
    param = p_obj._exeParam
    return param.replace("{i}", p_i).replace("{o}", p_o)


def slot_exe_run(ui):
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    exe = p_obj._exeDemo
    list_case = get_checked_items(p_obj._case, p_obj._eCaseCheck)
    if os.path.exists(exe):
        for case in list_case:
            param = generate_exe_param(ui, case)
            #QMessageBox.about(None, "Message", param)
            #continue
            in_param = param.split(" ")
            in_param.insert(0, exe)
            proc_demo = subprocess.Popen(in_param, cwd = os.path.dirname(exe))
            proc_demo.wait()
    ver = p_obj._eVer
    if ver in p_obj._ver:
        return
    p_obj._ver.append(ver)
    ui.fill_ui_info(p_obj)


def slot_new_project(ui):
    path, _ = QFileDialog.getSaveFileName(None, "Save New Project", "", "XML(*.xml)")
    if path is None or path == "":
        return
    p = project_io.Project()
    if os.path.splitext(path)[1] != ".xml":
        path += ".xml"
    p._configFile = path
    ui._p = p
    ui._p.save_xml(path)
    ui.fill_ui_info(ui._p)
    new_item = ptree_add_item(ui._pTree, path)
    ui.fill_proj_list()
    set_project_selected(ui._qlv_all_proj, new_item.attrib["name"])


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
    if path is None or path == "":
        return
    if not os.path.exists(path):
        QMessageBox.about(None, "Error", "Wrong file: {}!".format(path))
        return
    p = project_io.Project()
    p.load_xml(path)
    ui.fill_ui_info(p)
    new_item = ptree_add_item(ui._pTree, path)
    ui.fill_proj_list()
    set_project_selected(ui._qlv_all_proj, new_item.attrib["name"])
    return


def slot_scan_input(ui):
    # update project_object
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    dir_in = p_obj._dirInput
    p_obj._case = [f for f in os.listdir(dir_in)
                   if os.path.isdir(os.path.join(dir_in, f))]
    ui.fill_ui_info(p_obj)
    return


def append_input_to_list(l, label):
    text, ok = QInputDialog.getText(None, label, "Item list, seperate with ',':", QLineEdit.Normal, "")
    if ok and text != '':
        item_list = text.replace(" ", "").split(",")
        for i in item_list:
            l.append(i)
        return 0
    return 1


def slot_add_case(ui):
    ui._p = ui.collect_ui_info()
    if append_input_to_list(ui._p._case, "Case") == 0:
        ui.fill_ui_info(ui._p)
    return


def slot_add_ver(ui):
    ui._p = ui.collect_ui_info()
    if append_input_to_list(ui._p._ver, "Version") == 0:
        ui.fill_ui_info(ui._p)
    return


def slot_add_alg(ui):
    ui._p = ui.collect_ui_info()
    if append_input_to_list(ui._p._alg, "Algorithm") == 0:
        ui.fill_ui_info(ui._p)
    return


def slot_qlv_double_click(ui, qlv, qle):
    sl = qlv.selectedIndexes()
    if len(sl) < 1:
        return
    click_path = os.path.join(qle.text(), sl[0].data())
    if os.path.exists(click_path):
        os.startfile(click_path)
    return


def slot_ss_manage(ui):
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    # get dir
    sl = ui._qlv_ss_case.selectedIndexes()
    if len(sl) < 1:
        QMessageBox.about(None, "Tip:", "No Selected Item in CASE LIST to Manage!")
        return
    dir_case = os.path.join(p_obj._dirInput, sl[0].data())
    file_config = os.path.join(dir_case, "config.txt")
    if not os.path.exists(file_config):
        f= open(file_config, "w+")
        f.close()
    os.startfile(dir_case)


def slot_ss_preview(ui):
    ui._p = ui.collect_ui_info()
    p_obj = ui._p
    # get dir
    sl = ui._qlv_ss_case.selectedIndexes()
    if len(sl) < 1:
        QMessageBox.about(None, "Tip:", "No Selected Item in CASE LIST to Manage!")
        return
    case_name = sl[0].data()
    dir_case = os.path.join(p_obj._dirInput, case_name)
    file_config = os.path.join(dir_case, "config.txt")
    dir_i = p_obj._dirInput
    dir_o = p_obj._dirOutput
    # write to file
    filename = os.path.join(dir_o, "ss_config.txt")
    line_str = "cas {}\n".format(case_name) + "ver input\n" + "alg tmp"
    f_config = open(filename, "w")
    f_config.write(line_str + "\n")
    f_config.close()
    # run pvpython.exe
    exe_pvpython = p_obj._exePV
    if not os.path.exists(exe_pvpython):
        QMessageBox.about(None, "Error:", "PV interpator {} dose not exist!".format(exe_pvpython))
        return
    dir_pv_wd = os.path.dirname(exe_pvpython)
    py_ss = os.path.join(os.path.dirname(os.path.realpath(__file__)), "create_screenshots.py")
    proc_ss = subprocess.Popen(
        [exe_pvpython, py_ss,
         dir_i, dir_o, filename], cwd=dir_pv_wd)
    proc_ss.wait()
    first_pic = os.path.join(dir_o, case_name, "input")
    if os.path.exists(first_pic):
        os.startfile(first_pic)
    return


def load_ptree_obj(ui):
    dir_lp = os.path.dirname(os.path.realpath(__file__))
    file_lp = os.path.join(dir_lp, "tf_proj.xml")
    if not os.path.exists(file_lp):
        # create new xml
        root_new = ET.Element("projects")
        ui._pTree = ET.ElementTree(root_new)
        ui._pTree.write(file_lp)
    else:
        # has existing, load info
        ui._pTree = ET.parse(file_lp)


def save_ptree_obj(ui):
    dir_lp = os.path.dirname(os.path.realpath(__file__))
    file_lp = os.path.join(dir_lp, "tf_proj.xml")
    ui._pTree.write(file_lp)
    return


def slot_switch_proj(ui):
    sl = ui._qlv_all_proj.selectedIndexes()
    if len(sl) < 1:
        return
    # save old
    ui._p = ui.collect_ui_info()
    ui._p.save_xml(ui._p._configFile)
    # get new
    new_item = find_ptree_item(ui._pTree, sl[0].data())
    if new_item is None:
        return
    new_xml = new_item.attrib["path"]
    if not os.path.exists(new_xml):
        QMessageBox.about(None, "Error", "{} doesnot exist!".format(new_xml))
        return
    new_p = project_io.Project()
    new_p.load_xml(new_xml)
    ui._p = new_p
    ui.fill_ui_info(ui._p)


def slot_open_proj_path(ui):
    sl = ui._qlv_all_proj.selectedIndexes()
    if len(sl) < 1:
        return
    click_path = os.path.dirname(ui._p._configFile)
    if os.path.exists(click_path):
        os.startfile(click_path)
