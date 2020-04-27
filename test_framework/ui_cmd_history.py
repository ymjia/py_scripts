# -*- coding: utf-8 -*-
## @file ui_cmd_history.py
## @brief cmd history management
## @author jiayanming

import os.path
import datetime

import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QWidget, QGridLayout, QTreeView, QLabel, QDialog
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from test_framework.ui_logic import create_QListView
from test_framework.utils import indent_xml


class CMDHistory(QDialog):
    def __init__(self, qpt):
        QDialog.__init__(self)
        self.setWindowTitle("Command Line History")
        self.resize(800, 200)
        self._qlv_demo = create_QListView(self)
        self._qlv_demo.clicked.connect(self.slot_switch_demo)
        self._qtv_cmd = QTreeView(self)
        self._qtv_cmd.doubleClicked.connect(lambda: self.slot_update_cmd(qpt))
        grid = QGridLayout()
        grid.addWidget(QLabel("Demo Name"), 0, 0)
        grid.addWidget(self._qlv_demo, 1, 0)
        grid.addWidget(QLabel("CMD History, Double click to Use"), 0, 1)
        grid.addWidget(self._qtv_cmd, 1, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 4)
        self.setLayout(grid)
        self._file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "cmd_history.xml")
        self._cmdTree = ET.ElementTree()

    def create_xml(self):
        if not os.path.exists(self._file):
            dir_f = os.path.dirname(self._file)
            if not os.path.exists(dir_f):
                os.makedirs(dir_f)
            root_new = ET.Element("cmd_history")
            self._cmdTree = ET.ElementTree(root_new)
            indent_xml(root_new)
            self._cmdTree.write(self._file)

    def fill_list(self):
        # initial empty cmd history file
        self.create_xml()
        self._cmdTree = ET.parse(self._file)
        rt = self._cmdTree.getroot()
        self.fill_demo_list(rt)
        q_idx = self._qlv_demo.model().index(0, 0)
        if not q_idx.isValid():
            return
        self._qlv_demo.selectionModel().select(q_idx, QItemSelectionModel.Select)
        self.fill_cmd_list(rt.find(q_idx.data()))
        # set width
        self._qtv_cmd.setColumnWidth(0, 120)
        self._qtv_cmd.setColumnWidth(1, 120)
        self._qtv_cmd.setColumnWidth(2, 400)
        return

    def fill_demo_list(self, root):
        m = QStandardItemModel()
        flag = Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled
        for item in root:
            p_name = item.tag
            qsi = QStandardItem(p_name)
            qsi.setFlags(flag)
            qsi.setCheckable(False)
            m.appendRow(qsi)
        self._qlv_demo.setModel(m)

    # update cmd view
    def fill_cmd_list(self, root):
        m = QStandardItemModel()
        m.setColumnCount(3)
        m.setHeaderData(0, Qt.Horizontal, "Last Use");
        m.setHeaderData(1, Qt.Horizontal, "First Use");
        m.setHeaderData(2, Qt.Horizontal, "Cmd String");
        flag = Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled
        for item in root:
            i_time = QStandardItem(item.attrib["init_t"])
            l_time = QStandardItem(item.attrib["last_t"])
            name = QStandardItem(item.attrib["cmd"])
            i_time.setFlags(flag)
            l_time.setFlags(flag)
            name.setFlags(flag)
            m.appendRow([l_time, i_time, name])
        self._qtv_cmd.setModel(m)
        self._qtv_cmd.sortByColumn(0, Qt.DescendingOrder)

    def slot_switch_demo(self):
        sl = self._qlv_demo.selectedIndexes()
        if len(sl) < 1:
            return
        rt = self._cmdTree.getroot()
        demo = rt.find(sl[0].data())
        if demo is None:
            return
        self.fill_cmd_list(demo)

    # set main window text
    def slot_update_cmd(self, qpt):
        sl = self._qtv_cmd.selectedIndexes()
        if len(sl) < 1:
            return
        sel_row = sl[0].row()
        q_idx = self._qtv_cmd.model().index(sel_row, 2)
        qpt.setPlainText(q_idx.data())

    def add_cmd(self, exe, param):
        str_time = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        # get info
        stem = os.path.splitext(os.path.basename(exe))[0]
        # create file
        self.create_xml()
        self._cmdTree = ET.parse(self._file)
        rt = self._cmdTree.getroot()
        # add or find demo
        demo = rt.find(stem)
        if demo is None:
            demo = ET.Element(stem)
            rt.append(demo)
        # add or update cmd
        exist = False
        for item in demo:
            if item.attrib["cmd"] != param:
                continue
            item.attrib["last_t"] = str_time
            exist = True
            break;
        if not exist:
            demo.append(ET.Element(
                "item", {"last_t":str_time, "init_t":str_time, "cmd": param}))
        indent_xml(rt)
        self._cmdTree.write(self._file)
