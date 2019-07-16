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
        self._p = p_obj
        box = QVBoxLayout()
        box.addStretch(1)
        box.addWidget(self.create_project_info())
        # box.addWidget(self.create_project_info())
        box.addWidget(self.create_control_region())
        self.setLayout(box)
        self.setWindowTitle("Test Framework")
        self.resize(1500, 900)

    def create_project_info(self):
        view = QListView()
        return view

    def get_check_list(self, item_list, check_dict):
        lv_item = QListView()
        model = QStandardItemModel()
        for i in item_list:
            item = QStandardItem(i)
            check = Qt.Checked if i in check_dict else Qt.Unchecked
            item.setCheckState(check)
            item.setCheckable(True)
            model.appendRow(item)
        lv_item.setModel(model)
        return lv_item

    def create_control_region(self):
        control_region = QWidget()
        box = QHBoxLayout()
        box.addWidget(self.create_exe_region())
        box.addWidget(self.create_ss_region())
        box.addWidget(self.create_doc_region())
        control_region.setLayout(box)
        return control_region

    def create_exe_region(self):
        exe_region = QGroupBox("Executable Configuration")
        ql_exe = QLabel('Executable')
        ql_input = QLabel('Input')
        ql_output = QLabel('Output')
        ql_exeEdit = QLineEdit()
        ql_inputEdit = QLineEdit()
        ql_outputEdit = QLineEdit()
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_exe, 1, 0)
        grid.addWidget(ql_exeEdit, 1, 1)

        grid.addWidget(ql_input, 2, 0)
        grid.addWidget(ql_inputEdit, 2, 1)

        grid.addWidget(ql_output, 3, 0)
        grid.addWidget(ql_outputEdit, 3, 1)

        exe_region.setLayout(grid)
        exe_region.setGeometry(300, 300, 350, 300)
        return exe_region

    def create_ss_region(self):
        ss_region = QGroupBox("ScreenShot Configuration")
        ql_case = QLabel('Case')
        ql_alg = QLabel('Algorithm')
        ql_ver = QLabel('Version')
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_case, 1, 0)
        grid.addWidget(self.get_check_list(self._p._case, self._p._sCaseCheck), 1, 1)
        grid.addWidget(ql_alg, 2, 0)
        grid.addWidget(self.get_check_list(self._p._alg, self._p._sAlgCheck), 2, 1)
        grid.addWidget(ql_ver, 3, 0)
        grid.addWidget(self.get_check_list(self._p._ver, self._p._sVerCheck), 3, 1)
        ss_region.setLayout(grid)
        ss_region.setGeometry(300, 300, 350, 300)
        pybutton = QPushButton('Take Screenshot', self)
        pybutton.clicked.connect(lambda: ui_logic.create_screenshots(self._p))
        pybutton.resize(100, 32)
        return ss_region

    def create_doc_region(self):
        doc_region = QGroupBox("Docx Configuration")
        ql_case = QLabel('Case')
        ql_alg = QLabel('Algorithm')
        ql_ver = QLabel('Version')
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_case, 1, 0)
        grid.addWidget(self.get_check_list(self._p._case, self._p._dCaseCheck), 1, 1)
        grid.addWidget(ql_alg, 2, 0)
        grid.addWidget(self.get_check_list(self._p._alg, self._p._dAlgCheck), 2, 1)
        grid.addWidget(ql_ver, 3, 0)
        grid.addWidget(self.get_check_list(self._p._ver, self._p._dVerCheck), 3, 1)
        doc_region.setLayout(grid)
        doc_region.setGeometry(300, 300, 350, 300)
        pybutton = QPushButton('Generate Document', self)
        pybutton.clicked.connect(lambda: ui_logic.generate_docx("test", self._p))
        pybutton.resize(100, 32)
        return doc_region


p = project_io.Project("c:/data/test_framwork/management/project1/tf_config.xml")
p.load_project()

app = QApplication(sys.argv)
w = TFWindow(p)
w.show()
sys.exit(app.exec_())
