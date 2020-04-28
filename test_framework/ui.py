# -*- coding: utf-8 -*-
## @file ui.py
## @brief ui definition, transfer module between project_object and ui
## @author jiayanming

import os.path
import sys
import datetime
from pathlib import Path
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
from test_framework import thread_module
from test_framework.ui_logic import create_QListView
from test_framework.ui_configuration import GeneralConfigurationUI
from test_framework.ui_batch_exe import BatchManage
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
        self._ql_hist_exe = QLabel(str(utils.get_hist_item("exe")))
        self._ql_hist_ss = QLabel(str(utils.get_hist_item("ss")))
        self._ql_hist_doc = QLabel(str(utils.get_hist_item("doc")))
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
        self._configDialog = GeneralConfigurationUI(self)
        self._exportDialog = None
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
        self._cmdDialog = ui_cmd_history.CMDHistory(self._qpt_exe_param)

    def closeEvent(self, event):
        self.collect_ui_info()
        self._p.save_xml(self._p._configFile)

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
        d_in = cur_obj._dirInput
        d_out = cur_obj._dirOutput 
        if not os.path.exists(d_in) and cur_obj._rdirInput != "":
            # input not exists, try relative
            rel_root = str(Path(cur_obj._configFile).parent)
            rel_input = os.path.join(rel_root, cur_obj._rdirInput)
            if os.path.exists(rel_input):
                d_in = rel_input
                d_out = os.path.join(rel_root, cur_obj._rdirOutput)
        self._qle_dir_in.setText(d_in)
        self._qle_dir_out.setText(d_out)
        self._qle_exe_demo.setText(cur_obj._exeDemo)
        self._qle_doc_name.setText(cur_obj._docName)
        self._qcb_cur_ver.clear()
        self._qcb_doc_type.setCurrentText(in_obj._curDocType)

        for v in cur_obj._ver:
            self._qcb_cur_ver.addItem(v)
        self._qcb_cur_ver.setEditText(cur_obj._eVer)
        self._qpt_exe_param.setPlainText(cur_obj._exeParam)
        ui_logic.fill_check_list(self._qlv_exe_case, cur_obj._case, cur_obj._eCaseCheck)
        ui_logic.fill_check_list(self._qlv_ss_case, cur_obj._case, cur_obj._sCaseCheck)
        ui_logic.fill_check_list(self._qlv_ss_ver, cur_obj._ver, cur_obj._sVerCheck)
        ui_logic.fill_check_list(self._qlv_ss_alg, cur_obj._alg, cur_obj._sAlgCheck)
        ui_logic.fill_check_list(self._qlv_doc_case, cur_obj._case, cur_obj._dCaseCheck)
        ui_logic.fill_check_list(self._qlv_doc_ver, cur_obj._ver, cur_obj._dVerCheck)
        ui_logic.fill_check_list(self._qlv_doc_alg, cur_obj._alg, cur_obj._dAlgCheck)


    def collect_ui_info(self):
        out_obj = self._p
        out_obj._configFile = self._qle_conf_file.text()
        abs_in = self._qle_dir_in.text()
        abs_out = self._qle_dir_out.text()
        out_obj._dirInput = abs_in
        out_obj._dirOutput = abs_out
        # get valid relative path
        try:
            rel_root = str(Path(out_obj._configFile).parent)
            common_in = os.path.commonpath([out_obj._configFile, abs_in])
            common_out = os.path.commonpath([out_obj._configFile, abs_out])
            if rel_root == common_in and rel_root == common_out:
                out_obj._rdirInput = os.path.relpath(abs_in, rel_root)
                out_obj._rdirOutput = os.path.relpath(abs_out, rel_root)
        except ValueError:
            out_obj._rdirInput = ""
            out_obj._rdirOutput = ""
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

    def add_hist_item(self, hist_type, val):
        new_num = utils.add_hist_item(hist_type, val)
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
        qpb_export = QPushButton("Export Data")
        qpb_export.setStyleSheet("background-color:#9a9a9a")
        qpb_export.clicked.connect(self.slot_show_export)
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
        grid.addWidget(qpb_export, 4, 0)
        grid.addWidget(qpb_config, 4, 1)

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
        #qpb_add_ver.clicked.connect(lambda: ui_logic.slot_add_list(self, self._p._ver, "Version"))
        qpb_add_ver.clicked.connect(self.slot_add_ver_list)
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
        qpb_batch_config = QPushButton("Edit Batch")
        qpb_batch_run = QPushButton("Run Batch")
        qpb_exe_stop.setStyleSheet("background-color: red")
        qpb_exe_run.clicked.connect(lambda: ui_logic.slot_exe_run(self))
        qpb_exe_stop.clicked.connect(lambda: ui_logic.slot_exe_stop(self))
        qpb_exe_param.clicked.connect(lambda: ui_logic.slot_exe_param(self))
        qpb_batch_config.clicked.connect(self.slot_batch_config)
        qpb_batch_run.clicked.connect(self.slot_batch_run)
        # initial stack widget
        # 1st group
        self._qst_exe_param.addWidget(qpb_batch_run)
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
        grid.addWidget(qpb_batch_config, 4, 0)
        grid.addWidget(qpb_exe_param, 4, 1)
        grid.addWidget(self._qst_exe_param, 5, 0)
        grid.addWidget(self._qst_exe_button, 5, 1)
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
        #cmdDialog = ui_cmd_history.CMDHistory(self._qpt_exe_param)
        self._cmdDialog.fill_list()
        self._cmdDialog.exec_()

    def slot_show_config(self):
        self._configDialog.show()

    def slot_show_export(self):
        self.collect_ui_info()
        self._exportDialog = ProjectExporter(self._p)
        self._exportDialog.show()

    def slot_add_ver_list(self):
        cand = ui_logic.get_all_ver_names(self._p)
        alg_sel = FileNameSelector(cand, self._p._ver)
        alg_sel.exec_()
        self.fill_ui_info(self._p)

    def slot_add_alg_list(self):
        cand = ui_logic.get_all_filenames(self._p)
        alg_sel = FileNameSelector(cand, self._p._alg)
        alg_sel.exec_()
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

    def exe_finish(self, batch_mode=False):
        self.new_run_button()
        self._qlv_all_proj.setEnabled(True)
        self._ql_hist_exe.setText(str(utils.get_hist_item("exe")))
        case = self._p._case
        need_update = False
        if "plain_run" in case:
            need_update = True
        ver_list = []
        if batch_mode:
            for batch_item in self._p._batchList:
                ver_list.append(batch_item[2])
        else:
            ver_list.append(self._p._eVer)    
        for v in ver_list:
            if v != "" and v not in self._p._ver:
                self._p._ver.append(v)
                need_update = True
        if need_update:
            self.fill_ui_info(self._p)


    def slot_batch_config(self):
        batch_dialog = BatchManage(self._p)
        batch_dialog.exec_()
    
    def slot_batch_run(self):
        self.collect_ui_info()
        ss_exe = thread_module.ExeSession(self._p, True)
        self._cmdDialog.add_cmd([[item[0], item[1]] for item in self._p._batchList])
        self._threadExe = thread_module.ExeRunThread(ss_exe)
        self._threadExe.setTerminationEnabled()
        self._threadExe._sigProgress.connect(self.exe_progress)
        self._threadExe.finished.connect(lambda: self.exe_finish(True))
        self.new_stop_button()
        self._qlv_all_proj.setDisabled(True)
        self._threadExe.start()


class FileNameSelector(QDialog):
    def __init__(self, l_name, l_target):
        QDialog.__init__(self)
        self._listToAdd = l_target
        self._qlv_cand = create_QListView(self)
        self._qle_add = QLineEdit()
        self._qpb_add = QPushButton("Add")
        self._qpb_cancel = QPushButton("Cancel")
        self._qpb_add.clicked.connect(self.slot_add_to_list)
        self._qpb_cancel.clicked.connect(self.close)
        self.fill_cand_list(l_name)
        grid = QGridLayout()
        grid.addWidget(QLabel("Check existing Items in Output Directory:"))
        grid.addWidget(self._qlv_cand, 1, 0, 1, 2)
        grid.addWidget(QLabel("\nor\n\nInput Itmes FileName(seperate by ','):"))
        grid.addWidget(self._qle_add, 3, 0, 1, 2)
        grid.addWidget(self._qpb_add, 4, 0)
        grid.addWidget(self._qpb_cancel, 4, 1)
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
        for item in l_item:
            if item not in self._listToAdd:
                self._listToAdd.append(item)
        self.close()


class ProjectExporter(QDialog):
    def __init__(self, p_obj):
        QDialog.__init__(self)
        self._in_obj = p_obj
        self._out_obj = p_obj
        self._qlv_case = create_QListView(self)
        self._qlv_alg = create_QListView(self)
        self._qlv_ver = create_QListView(self)

        qpb_export = QPushButton("Export")
        qpb_cancel = QPushButton("Cancel")
        grid = QGridLayout()
        grid.addWidget(QLabel('Case'), 1, 0)
        grid.addWidget(self._qlv_case, 1, 1)
        grid.addWidget(QLabel('Version'), 2, 0)
        grid.addWidget(self._qlv_ver, 2, 1)
        grid.addWidget(QLabel('FileName'), 3, 0)
        grid.addWidget(self._qlv_alg, 3, 1)
        grid.addWidget(qpb_export, 4, 0)
        grid.addWidget(qpb_cancel, 4, 1)
        self.setLayout(grid)




if __name__ == "__main__":
    # create ui
    app = QApplication(sys.argv)
    w = TFWindow()
    w.show()
    sys.exit(app.exec_())
