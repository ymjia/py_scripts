# -*- coding: utf-8 -*-
## @file ui.py
## @brief ui updating
## @author jiayanming

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout,
                             QGroupBox, QListView, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

import os.path
import sys
sys.path.insert(0, r'c:/dev/py_scripts/')

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

    def load_proj_info(self, in_obj):
        self._p = in_obj

    def create_project_info(self):
        info = QGroupBox("Project Information")
        grid = QGridLayout()
        grid.setSpacing(10)
        self.get_f_bsw(self._qle_conf_file, grid, 0, "Configuration File")
        self.get_f_bsw(self._qle_dir_in, grid, 1, "Input Directory")
        self.get_f_bsw(self._qle_dir_out, grid, 2, "Output Directory")
        self.get_f_bsw(self._qle_exe_pv, grid, 3, "PVPython Interpreter")
        self.get_f_bsw(self._qle_exe_demo, grid, 4, "Demo Executable")
        info.setLayout(grid)
        info.setGeometry(300, 300, 350, 300)
        return info

    def get_check_list(self, lv, item_list, check_dict):
        model = QStandardItemModel()
        for i in item_list:
            item = QStandardItem(i)
            check = Qt.Checked if i in check_dict else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)
        lv.setModel(model)

    def create_control_region(self):
        control_region = QWidget()
        box = QHBoxLayout()
        box.addWidget(self.create_exe_region())
        box.addWidget(self.create_ss_region())
        box.addWidget(self.create_doc_region())
        control_region.setLayout(box)
        return control_region

    # create a file browser
    def get_f_bsw(self, qle, grid, grid_line, label):
        ql = QLabel(label)
        qpb = QPushButton("Browse..", self)
        grid.addWidget(ql, grid_line, 0)
        grid.addWidget(qle, grid_line, 1)
        grid.addWidget(qpb, grid_line, 2)

    def create_exe_region(self):
        exe_region = QGroupBox("Executable Configuration")
        ql_input = QLabel('Input Case')
        ql_ver = QLabel('Current Version Name')
        self.get_check_list(self._qlv_exe_case, self._p._case, self._p._dCaseCheck)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_input, 0, 0)
        grid.addWidget(self._qlv_exe_case, 0, 1)
        grid.addWidget(ql_ver, 1, 0)
        grid.addWidget(self._qle_cur_ver, 1, 1)
        exe_region.setLayout(grid)
        exe_region.setGeometry(300, 300, 350, 300)
        pybutton = QPushButton('RunDemo', self)
        #pybutton.clicked.connect(lambda: ui_logic.slot_create_screenshots(self._p))
        pybutton.resize(100, 32)
        grid.addWidget(pybutton, 2, 1)
        return exe_region

    def create_ss_region(self):
        ss_region = QGroupBox("ScreenShot Configuration")
        ql_case = QLabel('Case')
        ql_ver = QLabel('Version')
        ql_alg = QLabel('Algorithm')
        self.get_check_list(self._qlv_ss_case, self._p._case, self._p._sCaseCheck)
        self.get_check_list(self._qlv_ss_ver, self._p._ver, self._p._sVerCheck)
        self.get_check_list(self._qlv_ss_alg, self._p._alg, self._p._sAlgCheck)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_case, 1, 0)
        grid.addWidget(self._qlv_ss_case, 1, 1)
        grid.addWidget(ql_ver, 2, 0)
        grid.addWidget(self._qlv_ss_ver, 2, 1)
        grid.addWidget(ql_alg, 3, 0)
        grid.addWidget(self._qlv_ss_alg, 3, 1)
        ss_region.setLayout(grid)
        ss_region.setGeometry(300, 300, 350, 300)
        pybutton = QPushButton('Take Screenshot', self)
        pybutton.clicked.connect(lambda: ui_logic.slot_create_screenshots(self._p))
        pybutton.resize(100, 32)
        grid.addWidget(pybutton, 4, 1)
        return ss_region

    def create_doc_region(self):
        doc_region = QGroupBox("Docx Configuration")
        ql_case = QLabel('Case')
        ql_ver = QLabel('Version')
        ql_alg = QLabel('Algorithm')
        self.get_check_list(self._qlv_doc_case, self._p._case, self._p._dCaseCheck)
        self.get_check_list(self._qlv_doc_ver, self._p._ver, self._p._dVerCheck)
        self.get_check_list(self._qlv_doc_alg, self._p._alg, self._p._dAlgCheck)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_case, 1, 0)
        grid.addWidget(self._qlv_doc_case, 1, 1)
        grid.addWidget(ql_ver, 2, 0)
        grid.addWidget(self._qlv_doc_ver, 2, 1)
        grid.addWidget(ql_alg, 3, 0)
        grid.addWidget(self._qlv_doc_alg, 3, 1)
        doc_region.setLayout(grid)
        doc_region.setGeometry(300, 300, 350, 300)
        pybutton = QPushButton('Generate Document', self)
        pybutton.clicked.connect(lambda: ui_logic.slot_generate_docx("test", self._p))
        pybutton.resize(100, 32)
        grid.addWidget(pybutton, 4, 1)
        return doc_region


p = project_io.Project("c:/data/test_framwork/management/project1/tf_config.xml")
p.load_project()

app = QApplication(sys.argv)
w = TFWindow(p)
w._qle_conf_file.setText("config_file")
w.show()
sys.exit(app.exec_())
