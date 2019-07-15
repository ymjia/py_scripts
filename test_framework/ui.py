# -*- coding: utf-8 -*-
## @file ui.py
## @brief ui updating
## @author jiayanming

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGridLayout

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit
import os.path
import sys
sys.path.insert(0, r'c:/dev/py_scripts/')

import datetime
from test_framework import project_io
p = project_io.Project("c:/data/test_framwork/management/project1/tf_config.xml")


class TFWindow(QWidget):
    def __init__(self, parent = None):
        super(TFWindow, self).__init__(parent)
        box = QVBoxLayout()
        box.addWidget(self.create_project_info())
        box.addWidget(self.create_control_region())
        self.setLayout(box)
        self.setWindowTitle("Test Framework")
        self.resize(1500, 1200)


    def create_project_info(self):
        p_info = QWidget()
        return p_info

    def create_control_region(self):
        control_region = QWidget()
        box = QHBoxLayout()
        box.addWidget(self.create_exe_region())
        box.addWidget(self.create_ss_region())
        box.addWidget(self.create_doc_region())
        return control_region

    def create_exe_region(self):
        exe_region = QWidget()
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
        ss_region = QWidget()
        ql_case = QLabel('Case')
        ql_alg = QLabel('Algorithm')
        ql_ver = QLabel('Version')
        ql_caseEdit = QLineEdit()
        ql_algEdit = QLineEdit()
        ql_verEdit = QLineEdit()
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_case, 1, 0)
        grid.addWidget(ql_caseEdit, 1, 1)

        grid.addWidget(ql_alg, 2, 0)
        grid.addWidget(ql_algEdit, 2, 1)

        grid.addWidget(ql_ver, 3, 0)
        grid.addWidget(ql_verEdit, 3, 1)

        ss_region.setLayout(grid)
        ss_region.setGeometry(300, 300, 350, 300)
        return ss_region

    def create_doc_region(self):
        doc_region = QWidget()
        ql_case = QLabel('Case')
        ql_alg = QLabel('Algorithm')
        ql_ver = QLabel('Version')
        ql_caseEdit = QLineEdit()
        ql_algEdit = QLineEdit()
        ql_verEdit = QLineEdit()
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(ql_case, 1, 0)
        grid.addWidget(ql_caseEdit, 1, 1)

        grid.addWidget(ql_alg, 2, 0)
        grid.addWidget(ql_algEdit, 2, 1)

        grid.addWidget(ql_ver, 3, 0)
        grid.addWidget(ql_verEdit, 3, 1)

        doc_region.setLayout(grid)
        doc_region.setGeometry(300, 300, 350, 300)
        return doc_region


app = QApplication(sys.argv)
w = TFWindow()
w.show()
sys.exit(app.exec_())
