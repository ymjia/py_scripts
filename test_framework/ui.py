# -*- coding: utf-8 -*-
## @file ui.py
## @brief ui definition, transfer module between project_object and ui
## @author jiayanming

import os.path
import sys
import datetime

import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout,
                             QGroupBox, QListView, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPlainTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt, QItemSelection, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from test_framework import project_io
from test_framework import ui_logic


class TFWindow(QWidget):
    # take project object as input
    def __init__(self, parent=None):
        super(TFWindow, self).__init__(parent)
        self._ptName = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "tf_proj.xml")
            #os.getcwd(), "tf_proj.xml")
        self._p = project_io.Project()
        self._pTree = ET.ElementTree()
        # info widget for updating infomation
        # text
        self._qle_conf_file = QLineEdit()
        self._qle_dir_in = QLineEdit()
        self._qle_dir_out = QLineEdit()
        self._qle_exe_pv = QLineEdit()
        self._qle_exe_demo = QLineEdit()
        self._qle_cur_ver = QLineEdit()
        self._qle_doc_name = QLineEdit()
        self._qpt_exe_param = QPlainTextEdit()
        # listview
        self._qlv_all_proj = self.create_QListView()
        self._qlv_all_proj.clicked.connect(lambda: ui_logic.slot_switch_proj(self))
        self._qlv_all_proj.doubleClicked.connect(lambda: ui_logic.slot_open_proj_path(self))
        self._qlv_exe_case = self.create_QListView(self._qle_dir_in)
        self._qlv_ss_case = self.create_QListView(self._qle_dir_in)
        self._qlv_ss_alg = self.create_QListView()
        self._qlv_ss_ver = self.create_QListView()
        self._qlv_doc_case = self.create_QListView(self._qle_dir_out)
        self._qlv_doc_alg = self.create_QListView()
        self._qlv_doc_ver = self.create_QListView()
        self._qlv_ss_ver.doubleClicked.connect(lambda: ui_logic.slot_open_ss_ver(self))
        self._qlv_ss_alg.doubleClicked.connect(lambda: ui_logic.slot_open_ss_alg(self))
        self._qlv_doc_ver.doubleClicked.connect(lambda: ui_logic.slot_open_doc_ver(self))
        self._qlv_doc_alg.doubleClicked.connect(lambda: ui_logic.slot_open_doc_alg(self))
        
        # layout
        grid = QGridLayout()
        grid.addWidget(self.create_project_manage(), 0, 0, 3, 1)
        grid.addWidget(self.create_project_info(), 0, 1)
        grid.addWidget(self.create_list_manage(), 1, 1)
        grid.addWidget(self.create_control_region(), 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 3)
        self.setLayout(grid)
        self.setWindowTitle("Test Framework")
        self.resize(1024, 768)
        # initia data(fill objects)
        ui_logic.load_ptree_obj(self)
        self.fill_proj_list()

    def create_QListView(self, qle=None):
        ql = QListView()
        ql.setEditTriggers(QAbstractItemView.NoEditTriggers)
        if qle is not None:
            ql.doubleClicked.connect(lambda: ui_logic.slot_qlv_double_click(self, ql, qle))
        return ql

    def fill_proj_list(self):
        m = QStandardItemModel()
        for item in self._pTree.getroot():
            p_name = item.attrib["name"]
            qsi = QStandardItem(p_name)
            qsi.setCheckable(False)
            m.appendRow(qsi)
        self._qlv_all_proj.setModel(m)

    # load information from TFobject to ui
    def fill_ui_info(self, in_obj):
        self._p = in_obj
        cur_obj = self._p
        self._qle_conf_file.setText(cur_obj._configFile)
        self._qle_dir_in.setText(cur_obj._dirInput)
        self._qle_dir_out.setText(cur_obj._dirOutput)
        self._qle_exe_pv.setText(cur_obj._exePV)
        self._qle_exe_demo.setText(cur_obj._exeDemo)
        self._qle_doc_name.setText(cur_obj._docName)
        self._qle_cur_ver.setText(cur_obj._eVer)
        self._qpt_exe_param.setPlainText(cur_obj._exeParam)
        self.fill_check_list(self._qlv_exe_case, cur_obj._case, cur_obj._eCaseCheck)
        self.fill_check_list(self._qlv_ss_case, cur_obj._case, cur_obj._sCaseCheck)
        self.fill_check_list(self._qlv_ss_ver, cur_obj._ver, cur_obj._sVerCheck)
        self.fill_check_list(self._qlv_ss_alg, cur_obj._alg, cur_obj._sAlgCheck)
        self.fill_check_list(self._qlv_doc_case, cur_obj._case, cur_obj._dCaseCheck)
        self.fill_check_list(self._qlv_doc_ver, cur_obj._ver, cur_obj._dVerCheck)
        self.fill_check_list(self._qlv_doc_alg, cur_obj._alg, cur_obj._dAlgCheck)

    def collect_ui_info(self):
        out_obj = project_io.Project()
        out_obj._configFile = self._qle_conf_file.text()
        out_obj._dirInput = self._qle_dir_in.text()
        out_obj._dirOutput = self._qle_dir_out.text()
        out_obj._exePV = self._qle_exe_pv.text()
        out_obj._exeDemo = self._qle_exe_demo.text()
        out_obj._docName = self._qle_doc_name.text()
        out_obj._eVer = self._qle_cur_ver.text()
        out_obj._exeParam = self._qpt_exe_param.toPlainText()
        self.read_check_list(self._qlv_exe_case, out_obj._case, out_obj._eCaseCheck)
        self.read_check_list(self._qlv_ss_case, out_obj._case, out_obj._sCaseCheck)
        self.read_check_list(self._qlv_ss_ver, out_obj._ver, out_obj._sVerCheck)
        self.read_check_list(self._qlv_ss_alg, out_obj._alg, out_obj._sAlgCheck)
        self.read_check_list(self._qlv_doc_case, out_obj._case, out_obj._dCaseCheck)
        self.read_check_list(self._qlv_doc_ver, out_obj._ver, out_obj._dVerCheck)
        self.read_check_list(self._qlv_doc_alg, out_obj._alg, out_obj._dAlgCheck)
        return out_obj

    def create_project_manage(self):
        manage = QGroupBox("Project Manage")
        qpb_new = QPushButton("New Project")
        qpb_delete = QPushButton("Delete Project")
        qpb_save = QPushButton("Save Project")
        qpb_load = QPushButton("Load Project")
        qpb_new.clicked.connect(lambda: ui_logic.slot_new_project(self))
        qpb_delete.clicked.connect(lambda: ui_logic.slot_delete_project(self))
        qpb_save.clicked.connect(lambda: ui_logic.slot_save_project(self))
        qpb_load.clicked.connect(lambda: ui_logic.slot_load_project(self))
        grid = QGridLayout()
        grid.addWidget(self._qlv_all_proj, 0, 0, 1, 2)
        grid.addWidget(qpb_new, 1, 0)
        grid.addWidget(qpb_load, 1, 1)
        grid.addWidget(qpb_delete, 2, 0)
        grid.addWidget(qpb_save, 2, 1)
        manage.setLayout(grid)
        return manage

    def create_project_info(self):
        # fill information
        # create widget
        info = QGroupBox("Project Information")
        grid = QGridLayout()
        grid.setSpacing(10)
        self.get_f_bsw(self._qle_conf_file, grid, 0, "Configuration File", "xml")
        qpb_set_dir_in = QPushButton("Browse..")
        grid.addWidget(QLabel("Input Directory"), 1, 0)
        grid.addWidget(self._qle_dir_in, 1, 1)
        grid.addWidget(qpb_set_dir_in, 1, 2)
        qpb_set_dir_in.clicked.connect(lambda: ui_logic.slot_open_input_path(self))
        self.get_f_bsw(self._qle_dir_out, grid, 2, "Output Directory")
        self.get_f_bsw(self._qle_exe_pv, grid, 3, "PVPython Interpreter", "exe")
        self.get_f_bsw(self._qle_exe_demo, grid, 4, "Demo Executable", "exe")
        info.setLayout(grid)
        info.setGeometry(300, 300, 350, 300)
        return info

    def create_list_manage(self):
        lm = QGroupBox("List Manage")
        l_hb = QGridLayout()
        qpb_scan_input = QPushButton("Scan Input Dir")
        qpb_add_case = QPushButton("Add Case Item") 
        qpb_add_ver = QPushButton("Add Version Item")
        qpb_add_alg = QPushButton("Add FillName Item")
        qpb_del_case = QPushButton("Del Case Item") 
        qpb_del_ver = QPushButton("Del Version Item")
        qpb_del_alg = QPushButton("Del FillName Item")
        qpb_scan_input.clicked.connect(lambda: ui_logic.slot_scan_input(self))
        qpb_add_case.clicked.connect(lambda: ui_logic.slot_add_case(self))
        qpb_add_ver.clicked.connect(lambda: ui_logic.slot_add_ver(self))
        qpb_add_alg.clicked.connect(lambda: ui_logic.slot_add_alg(self))
        qpb_del_case.clicked.connect(lambda: ui_logic.slot_del_case(self))
        qpb_del_ver.clicked.connect(lambda: ui_logic.slot_del_ver(self))
        qpb_del_alg.clicked.connect(lambda: ui_logic.slot_del_alg(self))
        l_hb.addWidget(qpb_scan_input, 0, 0)
        l_hb.addWidget(qpb_add_case, 0, 1)
        l_hb.addWidget(qpb_add_ver, 0, 2)
        l_hb.addWidget(qpb_add_alg, 0, 3)
        l_hb.addWidget(qpb_del_case, 1, 1)
        l_hb.addWidget(qpb_del_ver, 1, 2)
        l_hb.addWidget(qpb_del_alg, 1, 3)
        lm.setLayout(l_hb)
        return lm

    # get listview from project_object
    def fill_check_list(self, lv, item_list, check_dict):
        model = QStandardItemModel()
        for i in item_list:
            item = QStandardItem(i)
            check = Qt.Checked if i in check_dict else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)
        lv.setModel(model)

    # get project_object info from listview
    def read_check_list(self, lv, item_list, check_dict):
        item_list.clear()
        check_dict.clear()
        model = lv.model()
        if model is None:
            return
        for index in range(model.rowCount()):
            item = model.item(index)
            text = item.text()
            item_list.append(text)
            if item.checkState() == Qt.Checked:
                check_dict[text] = 1

    def create_control_region(self):
        control_region = QWidget()
        box = QHBoxLayout()
        box.addWidget(self.create_exe_region())
        box.addWidget(self.create_ss_region())
        box.addWidget(self.create_doc_region())
        control_region.setLayout(box)
        return control_region

    # create a file browser
    def get_f_bsw(self, qle, grid, grid_line, label, f_type=""):
        qpb = QPushButton("Browse..", self)
        grid.addWidget(QLabel(label), grid_line, 0)
        grid.addWidget(qle, grid_line, 1)
        grid.addWidget(qpb, grid_line, 2)
        if f_type == "":
            qpb.clicked.connect(lambda: ui_logic.slot_get_path(qle))
        else:
            qpb.clicked.connect(lambda: ui_logic.slot_get_file(qle, f_type))

    def create_exe_region(self):
        exe_region = QGroupBox("Executable Configuration")
        qpb_exe_run = QPushButton('Run Demo', self)
        qpb_exe_run.clicked.connect(lambda: ui_logic.slot_exe_run(self))
        grid = QGridLayout()
        grid.addWidget(QLabel('Input Case'), 0, 0)
        grid.addWidget(self._qlv_exe_case, 0, 1)
        ql_param = QLabel("Parameter Line\n{i} for input\n{o} for output")
        ql_param.setWordWrap(True);
        grid.addWidget(ql_param, 1, 0)
        grid.addWidget(self._qpt_exe_param, 1, 1)
        grid.addWidget(QLabel('Use Version Name'), 2, 0)
        grid.addWidget(self._qle_cur_ver, 2, 1)
        grid.addWidget(qpb_exe_run, 3, 0, 1, 2)
        exe_region.setLayout(grid)
        return exe_region

    def create_ss_region(self):
        ss_region = QGroupBox("ScreenShot Configuration")
        qpb_ss_shot = QPushButton('Take Screenshot', self)
        qpb_ss_shot.clicked.connect(lambda: ui_logic.slot_create_screenshots(self))
        qpb_ss_manage = QPushButton('设置视角', self)
        qpb_ss_manage.clicked.connect(lambda: ui_logic.slot_ss_manage(self))
        qpb_ss_preview = QPushButton('截图预览', self)
        qpb_ss_preview.clicked.connect(lambda: ui_logic.slot_ss_preview(self))
        grid = QGridLayout()
        grid.addWidget(QLabel('Case'), 1, 0)
        grid.addWidget(self._qlv_ss_case, 1, 1)
        grid.addWidget(QLabel('Version'), 2, 0)
        grid.addWidget(self._qlv_ss_ver, 2, 1)
        grid.addWidget(QLabel('FileName'), 3, 0)
        grid.addWidget(self._qlv_ss_alg, 3, 1)
        grid.addWidget(qpb_ss_manage, 4, 0)
        grid.addWidget(qpb_ss_preview, 4, 1)
        grid.addWidget(qpb_ss_shot, 5, 0, 1, 2)
        ss_region.setLayout(grid)
        return ss_region

    def create_doc_region(self):
        doc_region = QGroupBox("Docx Configuration")
        qpb_g_doc = QPushButton('Generate Document', self)
        qpb_g_doc.clicked.connect(lambda: ui_logic.slot_generate_docx(self))
        qpb_o_doc = QPushButton('Open Document', self)
        qpb_o_doc.clicked.connect(lambda: ui_logic.slot_open_docx(self))
        qpb_o_path = QPushButton('Open Path', self)
        qpb_o_path.clicked.connect(lambda: ui_logic.slot_open_docx_path(self))
        grid = QGridLayout()
        grid.addWidget(QLabel('Case'), 1, 0)
        grid.addWidget(self._qlv_doc_case, 1, 1)
        grid.addWidget(QLabel('Version'), 2, 0)
        grid.addWidget(self._qlv_doc_ver, 2, 1)
        grid.addWidget(QLabel('FileName'), 3, 0)
        grid.addWidget(self._qlv_doc_alg, 3, 1)
        grid.addWidget(QLabel('FileName'), 3, 0)
        grid.addWidget(self._qlv_doc_alg, 3, 1)
        grid.addWidget(QLabel('Doc Name'), 4, 0)
        grid.addWidget(self._qle_doc_name, 4, 1)
        grid.addWidget(qpb_o_path, 5, 0)
        grid.addWidget(qpb_o_doc, 5, 1)
        grid.addWidget(qpb_g_doc, 6, 0, 1, 2)
        doc_region.setLayout(grid)
        return doc_region


if __name__ == "__main__":
    # create ui
    app = QApplication(sys.argv)
    w = TFWindow()
    w.show()
    sys.exit(app.exec_())
