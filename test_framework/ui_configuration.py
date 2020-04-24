# -*- coding: utf-8 -*-
## @file ui_configuration.py
## @brief general configuration management
## @author jiayanming

import os.path
from os import getcwd
import datetime
import sys
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QTreeView, QLabel,
                             QCheckBox, QLineEdit, QComboBox, QGroupBox, QPushButton,
                             QTabWidget)
from PyQt5.QtCore import Qt, QItemSelectionModel
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from test_framework.utils import g_config

class GeneralConfigurationUI(QWidget):
    #------------------------------------
    # screenshot
    #    force update
    #    view size
    #    specular, color, texture, trans_bg
    # docx
    #    #hd
    #    nominal/critial/max dist
    #    6 sigma
    #    legend 
    #
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.setWindowTitle("General Configurations")
        self._qcb_exe_auto_input = QCheckBox("Auto select file from case dir as Input", self)
        self._qcb_exe_input_depth = QComboBox() # input directory scan depth
        self._qcb_exe_input_depth.setEditable(False)
        self._qcb_exe_input_depth.addItems(["1", "2", "3"])

        self._qcb_ss_force_update = QCheckBox("Force Update Screenshot", self)
        self._qcb_ss_specular = QCheckBox("Specular", self)
        self._qcb_ss_enable_color = QCheckBox("Enable RGB Color if exists", self)
        self._qcb_ss_enable_texture = QCheckBox("Enable Texture if exists", self)
        self._qcb_ss_trans_bd = QCheckBox("Transparent Background", self)
        self._qle_ss_view_width = QLineEdit("1024")
        self._qle_ss_view_height = QLineEdit("768")
        self._qcb_ss_default_camera = QComboBox() # type of document to be generated
        self._qcb_ss_default_camera.setEditable(False)
        self._qcb_ss_default_camera.addItems(["4_quadrant", "6_axis"])
        self._qcb_ss_default_ref_dir = QComboBox() # type of document to be generated
        self._qcb_ss_default_ref_dir.setEditable(False)
        self._qcb_ss_default_ref_dir.addItems(["Input", "Output"])


        self._qcb_hd_std_sts = QCheckBox("Generate Standard Statistics Table", self)
        self._qcb_hd_dist_rate = QCheckBox("Generate Distance Rate Table", self)
        self._qcb_hd_6_sigma = QCheckBox("Generate 6-sigam Rate Table", self)
        self._qcb_hd_ss_table = QCheckBox("Generate Screenshot Table", self)
        self._qcb_hd_legend_type = QComboBox() # type of document to be generated
        self._qcb_hd_legend_type.setEditable(False)
        self._qcb_hd_legend_type.addItems(["Horizontal", "Vertical"])
        self._qle_hd_picture_scale = QLineEdit("1.0")
        self._qle_hd_nominal_dist = QLineEdit("0.03")
        self._qle_hd_critical_dist = QLineEdit("0.05")
        self._qle_hd_max_dist = QLineEdit("0.1")

        # other object
        qpb_save = QPushButton("Save")
        qpb_save.clicked.connect(self.slot_save_config)
        qpb_default = QPushButton("Reset To Default")
        qpb_default.clicked.connect(self.slot_load_default)
        qpb_close = QPushButton("Close")
        qpb_close.clicked.connect(self.close)
        qgb_exe = QGroupBox("Exe Batch Settings")
        qgl_exe = QGridLayout()
        qgl_exe.addWidget(self._qcb_exe_auto_input)
        qgl_exe.addWidget(QLabel("Max Depth in Input Dir Scanning"))
        qgl_exe.addWidget(self._qcb_exe_input_depth)
        qgb_exe.setLayout(qgl_exe)

        # screenshot general
        qgb_ss = QGroupBox("Generate ScreenShot Settings")
        qgl_ss = QGridLayout()
        qgl_ss.addWidget(QLabel("ScreenShot Width"))
        qgl_ss.addWidget(self._qle_ss_view_width)
        qgl_ss.addWidget(QLabel("ScreenShot Height"))
        qgl_ss.addWidget(self._qle_ss_view_height)
        qgl_ss.addWidget(self._qcb_ss_force_update)
        qgl_ss.addWidget(self._qcb_ss_specular)
        qgl_ss.addWidget(self._qcb_ss_enable_color)
        qgl_ss.addWidget(self._qcb_ss_enable_texture)
        qgl_ss.addWidget(self._qcb_ss_trans_bd)
        qgl_ss.addWidget(QLabel("Default Directory for Camera Setting Referencing Object"))
        qgl_ss.addWidget(self._qcb_ss_default_ref_dir)
        qgl_ss.addWidget(QLabel("Default Camera Angle Type"))
        qgl_ss.addWidget(self._qcb_ss_default_camera)
        qgb_ss.setLayout(qgl_ss)

        # hausdorff doc
        qgb_hd = QGroupBox("Hausdorff Distance Report Configuration")
        qgl_hd = QGridLayout()
        qgl_hd.addWidget(self._qcb_hd_std_sts)
        qgl_hd.addWidget(self._qcb_hd_dist_rate)
        qgl_hd.addWidget(self._qcb_hd_6_sigma)
        qgl_hd.addWidget(self._qcb_hd_ss_table)
        qgl_hd.addWidget(QLabel("Legend Direction"))
        qgl_hd.addWidget(self._qcb_hd_legend_type)
        qgl_hd.addWidget(QLabel("Screenshot Default Picture Scale"))
        qgl_hd.addWidget(self._qle_hd_picture_scale)
        qgl_hd.addWidget(QLabel("Max Nominal Distance"))
        qgl_hd.addWidget(self._qle_hd_nominal_dist)
        qgl_hd.addWidget(QLabel("Max Critical Distance"))
        qgl_hd.addWidget(self._qle_hd_critical_dist)
        qgl_hd.addWidget(QLabel("Max Search Distance"))
        qgl_hd.addWidget(self._qle_hd_max_dist)
        qgb_hd.setLayout(qgl_hd)

        # tabs
        # tab--general
        qwg_general = QWidget()
        qgl_general = QGridLayout()
        qgl_general.addWidget(qgb_exe)
        qgl_general.addWidget(qgb_ss)
        qwg_general.setLayout(qgl_general)
        # tab--hausdorff
        qwg_hd = QWidget()
        qgl_hd = QGridLayout()
        qgl_hd.addWidget(qgb_hd)
        qwg_hd.setLayout(qgl_hd)
        qtb_main = QTabWidget()
        qtb_main.addTab(qwg_general, "General")
        qtb_main.addTab(qwg_hd, "Deviation Report")

        # main
        qgl_conf = QGridLayout()
        qgl_conf.addWidget(qtb_main, 0, 0, 1, 2)
        qgl_conf.addWidget(qpb_save, 1, 0)
        qgl_conf.addWidget(qpb_default, 1, 1)
        qgl_conf.addWidget(qpb_close, 2, 0, 1, 2)
        self.setLayout(qgl_conf)
        # fill in current config
        self.fill_info(g_config)

    def slot_save_config(self):
        self.collect_info(g_config)
        g_config.write_to_file()

    def slot_load_default(self):
        g_config.read_default()
        self.fill_info(g_config)

    def collect_info(self, cfg_obj):
        cfg_obj._config.clear()
        cfg_obj._config["exe_auto_input"] = self._qcb_exe_auto_input.isChecked()
        cfg_obj._config["exe_input_depth"] = self._qcb_exe_input_depth.currentText()

        cfg_obj._config["ss_force_update"] = self._qcb_ss_force_update.isChecked()
        cfg_obj._config["ss_specular"] = self._qcb_ss_specular.isChecked()
        cfg_obj._config["ss_enable_color"] = self._qcb_ss_enable_color.isChecked()
        cfg_obj._config["ss_enable_texture"] = self._qcb_ss_enable_texture.isChecked()
        cfg_obj._config["ss_transparent_bg"] = self._qcb_ss_trans_bd.isChecked()
        cfg_obj._config["ss_view_width"] = self._qle_ss_view_width.text()
        cfg_obj._config["ss_view_height"] = self._qle_ss_view_height.text()
        cfg_obj._config["ss_default_reference_directory"] = self._qcb_ss_default_ref_dir.currentText()
        cfg_obj._config["ss_default_camera_type"] = self._qcb_ss_default_camera.currentText()

        cfg_obj._config["hd_standard_statistics"] = self._qcb_hd_std_sts.isChecked()
        cfg_obj._config["hd_distance_rate"] = self._qcb_hd_dist_rate.isChecked()
        cfg_obj._config["hd_6_sigma"] = self._qcb_hd_6_sigma.isChecked()
        cfg_obj._config["hd_screenshot_table"] = self._qcb_hd_ss_table.isChecked()
        cfg_obj._config["hd_legend_type"] = self._qcb_hd_legend_type.currentText()
        cfg_obj._config["hd_nominal_dist"] = self._qle_hd_nominal_dist.text()
        cfg_obj._config["hd_critical_dist"] = self._qle_hd_critical_dist.text()
        cfg_obj._config["hd_max_dist"] = self._qle_hd_max_dist.text()
        cfg_obj._config["hd_picture_scale"] = self._qle_hd_picture_scale.text()

    def fill_info(self, cfg_obj):
        self._qcb_exe_auto_input.setChecked(cfg_obj.config_val("exe_auto_input", True))
        self._qcb_exe_input_depth.setCurrentText(cfg_obj.config_val("exe_input_depth", "1"))

        self._qcb_ss_force_update.setChecked(cfg_obj.config_val("ss_force_update", False))
        self._qcb_ss_specular.setChecked(cfg_obj.config_val("ss_specular", True))
        self._qcb_ss_enable_color.setChecked(cfg_obj.config_val("ss_enable_color", False))
        self._qcb_ss_enable_texture.setChecked(cfg_obj.config_val("ss_enable_texture", False))
        self._qcb_ss_trans_bd.setChecked(cfg_obj.config_val("ss_transparent_bg", False))
        self._qle_ss_view_width.setText(cfg_obj.config_val("ss_view_width", "1024"))
        self._qle_ss_view_height.setText(cfg_obj.config_val("ss_view_height", "768"))
        self._qcb_ss_default_ref_dir.setCurrentText(cfg_obj.config_val("ss_default_reference_directory", "Input"))
        self._qcb_ss_default_camera.setCurrentText(cfg_obj.config_val("ss_default_camera_type", "4_quadrant"))

        self._qcb_hd_std_sts.setChecked(cfg_obj.config_val("hd_standard_statistics", True))
        self._qcb_hd_dist_rate.setChecked(cfg_obj.config_val("hd_distance_rate", True))
        self._qcb_hd_6_sigma.setChecked(cfg_obj.config_val("hd_6_sigma", True))
        self._qcb_hd_ss_table.setChecked(cfg_obj.config_val("hd_screenshot_table", True))
        self._qcb_hd_legend_type.setCurrentText(cfg_obj.config_val("hd_legend_type", "Vertical"))
        self._qle_hd_nominal_dist.setText(cfg_obj.config_val("hd_nominal_dist", "0.03"))
        self._qle_hd_critical_dist.setText(cfg_obj.config_val("hd_critical_dist", "0.05"))
        self._qle_hd_max_dist.setText(cfg_obj.config_val("hd_max_dist", "0.3"))
        self._qle_hd_picture_scale.setText(cfg_obj.config_val("hd_picture_scale", "1.0"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")
    w = GeneralConfigurationUI()
    w.show()
    sys.exit(app.exec_())
