# -*- coding: utf-8 -*-
## @file ui.py
## @brief ui definition, transfer module between project_object and ui
## @author jiayanming

import os.path
import sys
import datetime

import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QGridLayout,
                             QStackedWidget, QComboBox, QDialog,
                             QGroupBox, QListView, QHBoxLayout, QTreeView, QProgressBar,
                             QLabel, QLineEdit, QPlainTextEdit, QAbstractItemView)
from PyQt5.QtCore import Qt, QItemSelection, QItemSelectionModel, QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from test_framework import project_io
from test_framework import utils
from test_framework import ui_cmd_history
from test_framework import ui_logic
from test_framework.ui_logic import create_QListView
from test_framework.ui_configuration import GeneralConfigurationUI
class TFWindow(QWidget):
    # take project object as input
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self._threadExe = None
        self._threadSS = None
        self._ptName = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "tf_proj.xml")
        self._p = project_io.Project()
        self._pTree = ET.ElementTree()
        # widgets for multithread
        self._qst_exe_button = QStackedWidget()
        self._qst_exe_param = QStackedWidget()
        self._qpr_exe_progress = QProgressBar()
        self._qpr_exe_progress.setRange(0, 100)
        # info widget for updating infomation
        # history statistics
        self._ql_hist_exe = QLabel(str(self.get_hist_item("exe")))
        self._ql_hist_ss = QLabel(str(self.get_hist_item("ss")))
        self._ql_hist_doc = QLabel(str(self.get_hist_item("doc")))
        # text
        self._qle_proj_filter = QLineEdit() # filter to project list
        self._qle_proj_filter.setPlaceholderText("Search...")
        self._qle_proj_filter.textChanged.connect(lambda: ui_logic.slot_project_list_filter(self))
        self._qle_conf_file = QLineEdit()
        self._qle_dir_in = QLineEdit()
        self._qle_dir_out = QLineEdit()
        self._qle_exe_demo = QLineEdit()
        self._qcb_cur_ver = QComboBox()
        self._qcb_cur_ver.setEditable(True)
        self._qcb_cur_ver.lineEdit().setPlaceholderText("Input or Select..")
        self._qle_doc_name = QLineEdit()
        self._qpt_exe_param = QPlainTextEdit()
        self._qpt_exe_param.setPlaceholderText("Example: -i {i} -o {o}")
        # listview
        self._qlv_all_proj = create_QListView(self)
        self._qlv_all_proj.clicked.disconnect()
        self._qlv_all_proj.clicked.connect(lambda: ui_logic.slot_switch_proj(self))
        self._qlv_all_proj.doubleClicked.connect(lambda: ui_logic.slot_open_proj_path(self))
        self._qlv_exe_case = create_QListView(self, self._qle_dir_in)
        self._qlv_ss_case = create_QListView(self, self._qle_dir_out)
        self._qlv_ss_alg = create_QListView(self)
        self._qlv_ss_ver = create_QListView(self)
        self._qlv_doc_case = create_QListView(self, self._qle_dir_out)
        self._qlv_doc_alg = create_QListView(self)
        self._qlv_doc_ver = create_QListView(self)
        self._qlv_ss_ver.doubleClicked.connect(lambda: ui_logic.slot_open_ss_ver(self))
        self._qlv_ss_alg.doubleClicked.connect(lambda: ui_logic.slot_open_ss_alg(self))
        self._qlv_doc_ver.doubleClicked.connect(lambda: ui_logic.slot_open_doc_ver(self))
        self._qlv_doc_alg.doubleClicked.connect(lambda: ui_logic.slot_open_doc_alg(self))
        # doc type selector
        self._qcb_doc_type = QComboBox() # type of document to be generated
        self._qcb_doc_type.setEditable(False)
        self._qcb_doc_type.addItems(["Screenshots", "Time_statistics", "CPU_MEM_statistics", "Hausdorf_dist"])
        # other object
        self._cmdDialog = ui_cmd_history.CMDHistory(self._qpt_exe_param)
        self._configDialog = GeneralConfigurationUI(self)
        self._filenameSelector = None
        # layout
        grid = QGridLayout()
        grid.addWidget(self.create_history(), 0, 0)
        grid.addWidget(self.create_project_manage(), 1, 0, 2, 1)
        grid.addWidget(self.create_project_info(), 0, 1)
        grid.addWidget(self.create_list_manage(), 1, 1)
        grid.addWidget(self.create_control_region(), 2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 3)
        self.setLayout(grid)
        self.setWindowTitle("Test Framework")
        self.resize(1200, 800)
        ui_logic.load_ptree_obj(self)
        self.fill_proj_list()

    def fill_proj_list(self, flt = ""):
        m = QStandardItemModel()
        flag = Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled
        for item in self._pTree.getroot():
            p_name = item.attrib["name"]
            flt_pass = True
            if len(flt) > 0:
                sub_pname = p_name
                for c in flt:
                    pos = sub_pname.find(c)
                    if pos == -1:
                        flt_pass = False
                        break
                    else:
                        sub_pname = sub_pname[pos + 1:]
            if not flt_pass:
                continue
            qsi = QStandardItem(p_name)
            qsi.setFlags(flag)
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
        self._qle_exe_demo.setText(cur_obj._exeDemo)
        self._qle_doc_name.setText(cur_obj._docName)
        self._qcb_cur_ver.clear()
        self._qcb_doc_type.setCurrentText(in_obj._curDocType)

        for v in cur_obj._ver:
            self._qcb_cur_ver.addItem(v)
        self._qcb_cur_ver.setEditText(cur_obj._eVer)
        self._qpt_exe_param.setPlainText(cur_obj._exeParam)
        self.fill_check_list(self._qlv_exe_case, cur_obj._case, cur_obj._eCaseCheck)
        self.fill_check_list(self._qlv_ss_case, cur_obj._case, cur_obj._sCaseCheck)
        self.fill_check_list(self._qlv_ss_ver, cur_obj._ver, cur_obj._sVerCheck)
        self.fill_check_list(self._qlv_ss_alg, cur_obj._alg, cur_obj._sAlgCheck)
        self.fill_check_list(self._qlv_doc_case, cur_obj._case, cur_obj._dCaseCheck)
        self.fill_check_list(self._qlv_doc_ver, cur_obj._ver, cur_obj._dVerCheck)
        self.fill_check_list(self._qlv_doc_alg, cur_obj._alg, cur_obj._dAlgCheck)

    def collect_ui_info(self):
        #out_obj = project_io.Project()
        out_obj = self._p
        out_obj._configFile = self._qle_conf_file.text()
        out_obj._dirInput = self._qle_dir_in.text()
        out_obj._dirOutput = self._qle_dir_out.text()
        out_obj._exeDemo = self._qle_exe_demo.text()
        out_obj._docName = self._qle_doc_name.text()
        out_obj._eVer = self._qcb_cur_ver.currentText()
        out_obj._exeParam = self._qpt_exe_param.toPlainText()
        out_obj._curDocType = self._qcb_doc_type.currentText()
        self.read_check_list(self._qlv_exe_case, out_obj._case, out_obj._eCaseCheck)
        self.read_check_list(self._qlv_ss_case, out_obj._case, out_obj._sCaseCheck)
        self.read_check_list(self._qlv_ss_ver, out_obj._ver, out_obj._sVerCheck)
        self.read_check_list(self._qlv_ss_alg, out_obj._alg, out_obj._sAlgCheck)
        self.read_check_list(self._qlv_doc_case, out_obj._case, out_obj._dCaseCheck)
        self.read_check_list(self._qlv_doc_ver, out_obj._ver, out_obj._dVerCheck)
        self.read_check_list(self._qlv_doc_alg, out_obj._alg, out_obj._dAlgCheck)
        return out_obj

    def get_hist_item(self, hist_type):
        return int(float(utils.get_reg_item(hist_type)) + 0.1)

    def add_hist_item(self, hist_type, val):
        cur_num = self.get_hist_item(hist_type)
        new_num = str(cur_num + val)
        utils.set_reg_item(hist_type, new_num)
        if hist_type == "exe":
            self._ql_hist_exe.setText(new_num)
        elif hist_type == "ss":
            self._ql_hist_ss.setText(new_num)
        elif hist_type == "doc":
            self._ql_hist_doc.setText(new_num)

    def create_history(self):
        hist = QGroupBox("History Statistics")
        grid = QGridLayout()
        grid.addWidget(QLabel("Total Demo Run: "), 0, 0)
        grid.addWidget(self._ql_hist_exe, 0, 1)
        grid.addWidget(QLabel("Total ScreenShots: "), 1, 0)
        grid.addWidget(self._ql_hist_ss, 1, 1)
        grid.addWidget(QLabel("Total Docs: "), 2, 0)
        grid.addWidget(self._ql_hist_doc, 2, 1)
        hist.setLayout(grid)
        return hist


    def create_project_manage(self):
        manage = QGroupBox("Project Manage")
        qpb_new = QPushButton("New Project")
        qpb_new.setStyleSheet("background-color:#9a9a9a")
        qpb_delete = QPushButton("Delete Project")
        qpb_save = QPushButton("Save Project")
        qpb_load = QPushButton("Load Project")
        qpb_config = QPushButton("Global Configuration")
        qpb_config.clicked.connect(self.slot_show_config)
        qpb_new.clicked.connect(lambda: ui_logic.slot_new_project(self))
        qpb_delete.clicked.connect(lambda: ui_logic.slot_delete_project(self))
        qpb_save.clicked.connect(lambda: ui_logic.slot_save_project(self))
        qpb_load.clicked.connect(lambda: ui_logic.slot_load_project(self))
        grid = QGridLayout()
        grid.addWidget(self._qle_proj_filter, 0, 0, 1, 2)
        grid.addWidget(self._qlv_all_proj, 1, 0, 1, 2)
        grid.addWidget(qpb_new, 2, 0)
        grid.addWidget(qpb_load, 2, 1)
        grid.addWidget(qpb_delete, 3, 0)
        grid.addWidget(qpb_save, 3, 1)
        grid.addWidget(qpb_config, 4, 0, 1, 2)
        manage.setLayout(grid)
        return manage

    def create_project_info(self):
        # fill information
        # create widget
        info = QGroupBox("Project Information")
        grid = QGridLayout()
        self.get_f_bsw(self._qle_conf_file, grid, 0, "Configuration File", "xml")
        qpb_set_dir_in = QPushButton("Browse..")
        qpb_set_dir_in.setStyleSheet("background-color:#9a9a9a")
        qpb_open_dir_in = QPushButton("Open") 
        grid.addWidget(QLabel("Input Directory"), 1, 0)
        grid.addWidget(self._qle_dir_in, 1, 1)
        grid.addWidget(qpb_set_dir_in, 1, 2)
        grid.addWidget(qpb_open_dir_in, 1, 3)
        qpb_set_dir_in.clicked.connect(lambda: ui_logic.slot_open_input_path(self))
        qpb_open_dir_in.clicked.connect(lambda: ui_logic.slot_open_path(self._qle_dir_in))
        self.get_f_bsw(self._qle_dir_out, grid, 2, "Output Directory")
        self.get_f_bsw(self._qle_exe_demo, grid, 4, "Demo Executable", "exe")
        info.setLayout(grid)
        return info

    def create_list_manage(self):
        lm = QGroupBox("List Manage")
        l_hb = QGridLayout()
        qpb_scan_input = QPushButton("Scan Input Dir")
        qpb_build_output = QPushButton("Build Output Dir")
        qpb_add_case = QPushButton("Add Case Item") 
        qpb_add_ver = QPushButton("Add Version Item")
        qpb_add_alg = QPushButton("Add FillName Item")
        qpb_del_case = QPushButton("Del Case Item")
        qpb_del_ver = QPushButton("Del Version Item")
        qpb_del_alg = QPushButton("Del FillName Item")
        qpb_del_case.setStyleSheet("background-color:#c82508")
        qpb_del_ver.setStyleSheet("background-color:#c82508")
        qpb_del_alg.setStyleSheet("background-color:#c82508")
        qpb_scan_input.clicked.connect(lambda: ui_logic.slot_scan_input(self))
        qpb_build_output.clicked.connect(lambda: ui_logic.slot_build_output(self))
        qpb_add_case.clicked.connect(
            lambda: ui_logic.slot_add_list(self, self._p._case, "Case"))
        qpb_add_ver.clicked.connect(
            lambda: ui_logic.slot_add_list(self, self._p._ver, "Version"))
        qpb_add_alg.clicked.connect(self.slot_add_alg_list)
        qpb_del_case.clicked.connect(
            lambda: ui_logic.slot_del_list(self, self._qlv_ss_case, self._p._case))
        qpb_del_ver.clicked.connect(
            lambda: ui_logic.slot_del_list(self, self._qlv_ss_ver, self._p._ver))
        qpb_del_alg.clicked.connect(
            lambda: ui_logic.slot_del_list(self, self._qlv_ss_alg, self._p._alg))
        l_hb.addWidget(qpb_scan_input, 0, 0)
        l_hb.addWidget(qpb_add_case, 0, 1)
        l_hb.addWidget(qpb_add_ver, 0, 2)
        l_hb.addWidget(qpb_add_alg, 0, 3)
        l_hb.addWidget(qpb_build_output, 1, 0)
        l_hb.addWidget(qpb_del_case, 1, 1)
        l_hb.addWidget(qpb_del_ver, 1, 2)
        l_hb.addWidget(qpb_del_alg, 1, 3)
        lm.setLayout(l_hb)
        return lm

    # get listview from project_object
    def fill_check_list(self, lv, item_list, check_dict):
        model = QStandardItemModel()
        #pt_item = QStandardItem()
        flag = Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled
        for i in item_list:
            item = QStandardItem(i)
            item.setFlags(flag)
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
        qpb_open = QPushButton("Open", self)
        qpb_open.clicked.connect(lambda: ui_logic.slot_open_path(qle))
        grid.addWidget(QLabel(label), grid_line, 0)
        grid.addWidget(qle, grid_line, 1)
        grid.addWidget(qpb, grid_line, 2)
        grid.addWidget(qpb_open, grid_line, 3)
        if f_type == "":
            qpb.clicked.connect(lambda: ui_logic.slot_get_path(qle))
        else:
            qpb.clicked.connect(lambda: ui_logic.slot_get_file(qle, f_type))

    def create_exe_region(self):
        exe_region = QGroupBox("Executable Configuration")
        qpb_cmd_his = QPushButton("历史命令", self)
        qpb_cmd_his.clicked.connect(self.slot_show_cmd_history)

        qpb_exe_run = QPushButton('Run Demo')
        qpb_exe_stop = QPushButton('中断')
        qpb_exe_param = QPushButton("命令预览", self)
        qpb_exe_stop.setStyleSheet("background-color: red")
        qpb_exe_run.clicked.connect(lambda: ui_logic.slot_exe_run(self))
        qpb_exe_stop.clicked.connect(lambda: ui_logic.slot_exe_stop(self))
        qpb_exe_param.clicked.connect(lambda: ui_logic.slot_exe_param(self))
        # initial stack widget
        # 1st group
        self._qst_exe_param.addWidget(qpb_exe_param)
        self._qst_exe_button.addWidget(qpb_exe_run)
        # 2nd group
        self._qst_exe_param.addWidget(self._qpr_exe_progress)
        self._qst_exe_button.addWidget(qpb_exe_stop)
        # initi group
        self._qst_exe_param.setCurrentIndex(0)
        self._qst_exe_button.setCurrentIndex(0)
        
        grid = QGridLayout()
        grid.addWidget(QLabel('Input Case'), 0, 0)
        grid.addWidget(self._qlv_exe_case, 0, 1)
        grid.addWidget(QLabel("Parameter Line\nPlace holders:\n{i} - input\n{o} - output\n{c} - case\n{v} - version name"), 1, 0)
        grid.addWidget(qpb_cmd_his, 2, 0)
        grid.addWidget(self._qpt_exe_param, 1, 1, 2, 1)
        grid.addWidget(QLabel('Use Version Name'), 3, 0)
        grid.addWidget(self._qcb_cur_ver, 3, 1)
        grid.addWidget(self._qst_exe_param, 4, 0)
        grid.addWidget(self._qst_exe_button, 4, 1)
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
        qpb_g_doc = QPushButton('Generate Doc', self)
        qpb_g_doc.clicked.connect(lambda: ui_logic.slot_generate_docx(self))
        # qpb_gt_doc = QPushButton('Time Docx', self)
        # qpb_gt_doc.clicked.connect(lambda: ui_logic.slot_generate_time_docx(self))
        # qpb_gp_doc = QPushButton('Proc Docx', self)
        # qpb_gp_doc.clicked.connect(lambda: ui_logic.slot_generate_proc_docx(self))
        qpb_o_doc = QPushButton('Open Document', self)
        qpb_o_doc.clicked.connect(lambda: ui_logic.slot_open_docx(self))
        qpb_o_path = QPushButton('Open Path', self)
        qpb_o_path.clicked.connect(lambda: ui_logic.slot_open_docx_path(self))
        qw_doc = QWidget()
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        # hbox.addWidget(qpb_gt_doc)
        # hbox.addWidget(qpb_gp_doc)
        hbox.addWidget(self._qcb_doc_type)
        hbox.addWidget(qpb_g_doc)
        qw_doc.setLayout(hbox)
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
        grid.addWidget(qw_doc, 6, 0, 1, 2)
        doc_region.setLayout(grid)
        return doc_region

    def slot_show_cmd_history(self):
        self._cmdDialog.resize(800, 200)
        self._cmdDialog.fill_list()
        self._cmdDialog.show()

    def slot_show_config(self):
        #self._configDialog.resize(800, 200)
        self._configDialog.show()

    def slot_add_alg_list(self):
        cand = ui_logic.get_all_filenames(self._p)
        self._filenameSelector = FileNameSelector(self, cand)
        self._filenameSelector.exec_()
        self.fill_ui_info(self._p)

    # button status switch
    def new_run_button(self):
        self._qst_exe_button.setCurrentIndex(0)
        self._qst_exe_param.setCurrentIndex(0)


    def new_stop_button(self):
        self._qst_exe_button.setCurrentIndex(1)
        self._qst_exe_param.setCurrentIndex(1)


    def exe_progress(self, p):
        self._qpr_exe_progress.setValue(p)

    def exe_finish(self):
        self.new_run_button()
        self._qlv_all_proj.setEnabled(True)


class FileNameSelector(QDialog):
    def __init__(self, parent, l_name):
        QDialog.__init__(self)
        self._mainWindow = parent
        self._qlv_cand = create_QListView(self)
        self._qle_add = QLineEdit()
        self._qpb_add = QPushButton("Add")
        self._qpb_cancel = QPushButton("Cancel")
        self._qpb_add.clicked.connect(self.slot_add_to_list)
        self._qpb_cancel.clicked.connect(self.close)
        self.fill_cand_list(l_name)
        grid = QGridLayout()
        grid.addWidget(self._qlv_cand, 0, 0, 1, 2)
        grid.addWidget(self._qle_add, 1, 0, 1, 2)
        grid.addWidget(self._qpb_add, 2, 0)
        grid.addWidget(self._qpb_cancel, 2, 1)
        self.setLayout(grid)

    def fill_cand_list(self, l_name):
        model = QStandardItemModel()
        flag = Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEnabled
        for i in l_name:
            item = QStandardItem(i)
            item.setFlags(flag)
            item.setCheckState(Qt.Unchecked)
            item.setCheckable(True)
            model.appendRow(item)
        self._qlv_cand.setModel(model)

    def slot_add_to_list(self):
        l_item = []
        model = self._qlv_cand.model()
        if model is None:
            return
        for index in range(model.rowCount()):
            item = model.item(index)
            if item.checkState() == Qt.Checked:
                l_item.append(item.text())
        text = self._qle_add.text()
        if text != "":
            text_list = text.replace(" ", "").split(",")
            for i in text_list:
                if i not in l_item:
                    l_item.append(i)
        p_obj = self._mainWindow._p
        for item in l_item:
            if item not in p_obj._alg:
                p_obj._alg.append(item)
        self.close()

if __name__ == "__main__":
    # create ui
    app = QApplication(sys.argv)
    w = TFWindow()
    w.show()
    sys.exit(app.exec_())
