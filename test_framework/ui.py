# -*- coding: utf-8 -*-
## @file ui.py
## @brief ui definition, transfer module between project_object and ui
## @author jiayanming

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout,
                             QGroupBox, QListView, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPlainTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import os.path
import sys
sys.path.insert(0, r'c:/dev/py_scripts/')
from test_framework import project_io
import datetime
from test_framework import project_io
from test_framework import ui_logic


class TFWindow(QWidget):
    # take project object as input
    def __init__(self, p_obj, parent=None):
        super(TFWindow, self).__init__(parent)
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
        self._qlv_exe_case = QListView()
        self._qlv_ss_case = QListView()
        self._qlv_ss_alg = QListView()
        self._qlv_ss_ver = QListView()
        self._qlv_doc_case = QListView()
        self._qlv_doc_alg = QListView()
        self._qlv_doc_ver = QListView()
        self._p = p_obj
        box = QVBoxLayout()
        box.addStretch(1)
        box.addWidget(self.create_project_info())
        box.addWidget(self.create_control_region())
        self.setLayout(box)
        self.setWindowTitle("Test Framework")
        self.resize(1024, 768)

    # load information from TFobject to ui
    def load_proj_info(self, in_obj=None):
        if in_obj is not None:
            self._p = in_obj
        cur_obj = self._p
        self._qle_conf_file.setText(cur_obj._configFile)
        self._qle_dir_in.setText(cur_obj._dirInput)
        self._qle_dir_out.setText(cur_obj._dirOutput)
        self._qle_exe_pv.setText(cur_obj._exePV)
        self._qle_exe_demo.setText(cur_obj._exeDemo)
        self._qle_doc_name.setText(cur_obj._docName)
        self._qle_cur_ver.setText(cur_obj._eVer)
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
        self.read_check_list(self._qlv_exe_case, out_obj._case, out_obj._eCaseCheck)
        self.read_check_list(self._qlv_ss_case, out_obj._case, out_obj._sCaseCheck)
        self.read_check_list(self._qlv_ss_ver, out_obj._ver, out_obj._sVerCheck)
        self.read_check_list(self._qlv_ss_alg, out_obj._alg, out_obj._sAlgCheck)
        self.read_check_list(self._qlv_doc_case, out_obj._case, out_obj._dCaseCheck)
        self.read_check_list(self._qlv_doc_ver, out_obj._ver, out_obj._dVerCheck)
        self.read_check_list(self._qlv_doc_alg, out_obj._alg, out_obj._dAlgCheck)
        return out_obj

    def create_project_info(self):
        # fill information
        # create widget
        info = QGroupBox("Project Information")
        grid = QGridLayout()
        grid.setSpacing(10)
        self.get_f_bsw(self._qle_conf_file, grid, 0, "Configuration File", "xml")
        self.get_f_bsw(self._qle_dir_in, grid, 1, "Input Directory")
        self.get_f_bsw(self._qle_dir_out, grid, 2, "Output Directory")
        self.get_f_bsw(self._qle_exe_pv, grid, 3, "PVPython Interpreter", "exe")
        self.get_f_bsw(self._qle_exe_demo, grid, 4, "Demo Executable", "exe")
        info.setLayout(grid)
        info.setGeometry(300, 300, 350, 300)
        return info

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
        qpb_exe_run.resize(100, 32)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel('Input Case'), 0, 0)
        grid.addWidget(self._qlv_exe_case, 0, 1)
        grid.addWidget(QLabel('Exe Parameter line'), 1, 0)
        grid.addWidget(self._qpt_exe_param, 1, 1)
        grid.addWidget(QLabel('Current Version Name'), 2, 0)
        grid.addWidget(self._qle_cur_ver, 2, 1)
        grid.addWidget(qpb_exe_run, 3, 1)
        exe_region.setLayout(grid)
        exe_region.setGeometry(300, 300, 350, 300)
        return exe_region

    def create_ss_region(self):
        ss_region = QGroupBox("ScreenShot Configuration")
        qpb_ss_shot = QPushButton('Take Screenshot', self)
        qpb_ss_shot.clicked.connect(lambda: ui_logic.slot_create_screenshots(self))
        qpb_ss_shot.resize(100, 32)
        qpb_ss_manage = QPushButton('Manage Screen Camera', self)
        qpb_ss_shot.clicked.connect(lambda: ui_logic.slot_create_screenshots(self))
        qpb_ss_manage.resize(100, 32)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel('Case'), 1, 0)
        grid.addWidget(self._qlv_ss_case, 1, 1)
        grid.addWidget(QLabel('Version'), 2, 0)
        grid.addWidget(self._qlv_ss_ver, 2, 1)
        grid.addWidget(QLabel('Algorithm'), 3, 0)
        grid.addWidget(self._qlv_ss_alg, 3, 1)
        grid.addWidget(qpb_ss_manage, 4, 1)
        grid.addWidget(qpb_ss_shot, 5, 1)
        ss_region.setLayout(grid)
        ss_region.setGeometry(300, 300, 350, 300)
        return ss_region

    def create_doc_region(self):
        doc_region = QGroupBox("Docx Configuration")
        qpb_g_doc = QPushButton('Generate Document', self)
        qpb_g_doc.clicked.connect(lambda: ui_logic.slot_generate_docx(self))
        qpb_g_doc.resize(100, 32)
        qpb_o_doc = QPushButton('Open Document', self)
        qpb_o_doc.clicked.connect(lambda: ui_logic.slot_open_docx(self))
        qpb_o_doc.resize(100, 32)
        qpb_o_path = QPushButton('Open Path', self)
        qpb_o_path.clicked.connect(lambda: ui_logic.slot_open_docx_path(self))
        qpb_o_path.resize(100, 32)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(QLabel('Case'), 1, 0)
        grid.addWidget(self._qlv_doc_case, 1, 1)
        grid.addWidget(QLabel('Version'), 2, 0)
        grid.addWidget(self._qlv_doc_ver, 2, 1)
        grid.addWidget(QLabel('Algorithm'), 3, 0)
        grid.addWidget(self._qlv_doc_alg, 3, 1)
        grid.addWidget(QLabel('Algorithm'), 3, 0)
        grid.addWidget(self._qlv_doc_alg, 3, 1)
        grid.addWidget(QLabel('Doc Name'), 4, 0)
        grid.addWidget(self._qle_doc_name, 4, 1)
        grid.addWidget(qpb_o_path, 5, 0)
        grid.addWidget(qpb_o_doc, 5, 1)
        grid.addWidget(qpb_g_doc, 6, 1)
        doc_region.setLayout(grid)
        doc_region.setGeometry(300, 300, 350, 300)
        return doc_region


p = project_io.Project("c:/dev/py_scripts/test_framework/tf_config.xml")
p.load_project()

app = QApplication(sys.argv)
w = TFWindow(p)
w.load_proj_info()
w.show()
sys.exit(app.exec_())
