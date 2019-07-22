# -*- coding: utf-8 -*-
## @file tf_main.py
## @brief test framework entry point
## @author jiayanming


import sys
import os
from PyQt5.QtWidgets import QApplication


sys.path.insert(0, os.getcwd())
from test_framework import ui

# create ui
app = QApplication(sys.argv)
w = ui.TFWindow()
w.show()
sys.exit(app.exec_())
