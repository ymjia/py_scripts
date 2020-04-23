# -*- coding: utf-8 -*-
## @file demo.py
## @brief pyqt test demo

import os
import sys
from PyQt5.QtWidgets import QApplication

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout,
                             QStackedWidget, QComboBox, QDialog, QSizePolicy,
                             QGroupBox, QListView, QHBoxLayout, QTreeView, QProgressBar,
                             QLabel, QLineEdit, QPlainTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt, QItemSelection, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class TestWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.resize(1200, 800)
        qgl_main = QGridLayout()
        self._qst_test = QStackedWidget()
        qpb_run = QPushButton("Run")
        #self._qst_test.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        qpb_stop = QPushButton("Stop")
        qpb_run.clicked.connect(self.slot_run)
        qpb_stop.clicked.connect(self.slot_stop)
        self._qpr_pg = QProgressBar()
        self._qpr_pg.setRange(0, 100)
        qhl = QHBoxLayout()
        qhl.addWidget(self._qpr_pg)
        qhl.addWidget(qpb_stop)
        qwg = QWidget()
        qwg.setLayout(qhl)
        self._qst_test.addWidget(qpb_run)
        self._qst_test.addWidget(qwg)
        qgl_main.addWidget(self._qst_test)
        self.setLayout(qgl_main)

    def slot_run(self):
        self._qst_test.setCurrentIndex(1)

    def slot_stop(self):
        self._qst_test.setCurrentIndex(0)


app = QApplication(sys.argv)
app.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")
w = TestWindow()
w.show()
sys.exit(app.exec_())
