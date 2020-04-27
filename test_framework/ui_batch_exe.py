# -*- coding: utf-8 -*-
## @file ui_batch_exe.py
## @brief exe batch management
## @author jiayanming

import os.path
import datetime

import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (QWidget, QGridLayout, QTreeView, QLabel, QLineEdit, QGroupBox,
                             QPlainTextEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                             QMessageBox, QComboBox, QDialog)
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from test_framework.ui_cmd_history import CMDHistory
from test_framework.ui_logic import slot_get_file
from test_framework.utils import indent_xml

# take project object as input, only change batch list
class BatchManage(QDialog):
    def __init__(self, p_obj):
        QDialog.__init__(self)
        self.setWindowTitle("Batch Exe Edit")
        self.resize(800, 600)
        self._batchList = p_obj._batchList
        self._qtv_item = QTreeView(self)
        self._qtv_item.doubleClicked.connect(self.slot_fill_info)
        self._qle_exe = QLineEdit()
        self._qpt_cmd = QPlainTextEdit()
        self._qcb_ver = QComboBox()
        # set initial value
        self._qle_exe.setText(p_obj._exeDemo)
        self._qpt_cmd.setPlainText(p_obj._exeParam)
        self._qcb_ver.setEditable(True)
        self._qcb_ver.setEditText(p_obj._eVer)
        for v in p_obj._ver:
            self._qcb_ver.addItem(v)

        qpb_exe = QPushButton("Browse...")
        qpb_cmd_his = QPushButton("CMD History")
        qpb_add = QPushButton("Add to List")
        qpb_del = QPushButton("Remove selected List")
        qpb_close = QPushButton("Close")
        qpb_exe.clicked.connect(lambda: slot_get_file(self._qle_exe, "exe"))
        qpb_cmd_his.clicked.connect(self.slot_cmd_hist)
        qpb_add.clicked.connect(self.slot_add_item)
        qpb_del.clicked.connect(self.slot_del_item)
        qpb_close.clicked.connect(self.close)

        qwg_exe = QWidget()
        qhb = QHBoxLayout()
        qhb.addWidget(self._qle_exe)
        qhb.addWidget(qpb_exe)
        qwg_exe.setLayout(qhb)

        qwg_cmd = QWidget()
        qhb = QHBoxLayout()
        qhb.addWidget(self._qpt_cmd)
        qhb.addWidget(qpb_cmd_his)
        qwg_cmd.setLayout(qhb)

        qwg_btn = QWidget()
        qhb = QHBoxLayout()
        qhb.addWidget(qpb_add)
        qhb.addWidget(qpb_del)
        qhb.addWidget(qpb_close)
        qwg_btn.setLayout(qhb)
        
        qgb_edit = QGroupBox("Add New Batch List Item")
        grid = QGridLayout()
        grid.addWidget(QLabel("Executable:"), 0, 0)
        grid.addWidget(qwg_exe, 0, 1)
        grid.addWidget(QLabel("Executable Command Line:"), 1, 0)
        grid.addWidget(qwg_cmd)
        grid.addWidget(QLabel("Use Version Name:"), 2, 0)
        grid.addWidget(self._qcb_ver, 2, 1)
        qgb_edit.setLayout(grid)

        l_main = QVBoxLayout()
        l_main.addWidget(QLabel("Existing batch list:"))
        l_main.addWidget(self._qtv_item)
        l_main.addWidget(qgb_edit)
        l_main.addWidget(qwg_btn)
        self.setLayout(l_main)
        #grid.setColumnStretch(0, 1)
        #grid.setColumnStretch(1, 4)

        #self._file = os.path.join(
        #    os.path.dirname(os.path.realpath(__file__)), "cmd_history.xml")
        #self._cmdTree = ET.ElementTree()
        self.fill_batch_list()

    # update cmd view
    def fill_batch_list(self):
        m = QStandardItemModel()
        m.setColumnCount(4)
        m.setHeaderData(0, Qt.Horizontal, "Executable");
        m.setHeaderData(1, Qt.Horizontal, "exe_full");
        m.setHeaderData(2, Qt.Horizontal, "Commnd Line");
        m.setHeaderData(3, Qt.Horizontal, "Version");
        flag = Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled
        for item in self._batchList:
            exe_short = QStandardItem(os.path.basename(item[0]))
            exe = QStandardItem(item[0])
            cmd = QStandardItem(item[1])
            ver = QStandardItem(item[2])
            exe.setFlags(flag)
            exe_short.setFlags(flag)
            cmd.setFlags(flag)
            ver.setFlags(flag)
            m.appendRow([exe_short, exe, cmd, ver])
        self._qtv_item.setModel(m)
        self._qtv_item.setColumnHidden(1, True)
        self._qtv_item.setColumnWidth(0, 120)
        self._qtv_item.setColumnWidth(2, 400)
        self._qtv_item.setColumnWidth(3, 120)

    def collect_batch_list(self):
        md = self._qtv_item.model()
        if md is None:
            return
        self._batchList.clear()
        for idx in range(md.rowCount()):
            self._batchList.append([md.index(idx, c).data() for c in range(1, 4)])

    # set main window text
    def slot_fill_info(self):
        sl = self._qtv_item.selectedIndexes()
        if len(sl) < 1:
            return
        sel_row = sl[0].row()
        md = self._qtv_item.model()
        self._qle_exe.setText(md.index(sel_row, 1).data())
        self._qpt_cmd.setPlainText(md.index(sel_row, 2).data())
        self._qcb_ver.setCurrentText(md.index(sel_row, 3).data())

    def slot_add_item(self):
        exe = self._qle_exe.text()
        cmd = self._qpt_cmd.toPlainText()
        ver = self._qcb_ver.currentText()
        self._batchList.append([exe, cmd, ver])
        self.fill_batch_list()

    def slot_del_item(self):
        # delete item in object and re fill ui
        sl = self._qtv_item.selectedIndexes()
        if len(sl) < 1:
            QMessageBox.about(self, "Message", "No Selected Item!")
            return
        self.collect_batch_list()
        for s in sl:
            print(s.row())

    def slot_cmd_hist(self):
        cmdDialog = CMDHistory(self._qpt_cmd)
        cmdDialog.fill_list()
        cmdDialog.exec_()
