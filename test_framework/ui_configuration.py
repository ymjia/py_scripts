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
                             QCheckBox, QLineEdit, QComboBox, QGroupBox, QPushButton)
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
        self._qcb_force_update = QCheckBox("Force Update Screenshot", self)
        self._qcb_specular = QCheckBox("Specular", self)
        self._qcb_enable_color = QCheckBox("Enable RGB Color if exists", self)
        self._qcb_enable_texture = QCheckBox("Enable Texture if exists", self)
        self._qcb_trans_bd = QCheckBox("Transparent Background", self)
        self._qle_view_width = QLineEdit("1024")
        self._qle_view_height = QLineEdit("768")

        self._qcb_hd_6_sigma = QCheckBox("Generate 6-sigam rate table", self)
        self._qcb_hd_legend_type = QComboBox() # type of document to be generated
        self._qcb_hd_legend_type.setEditable(False)
        self._qcb_hd_legend_type.addItems(["Horizontal", "Vertical"])
        self._qle_hd_nominal_dist = QLineEdit("0.03")
        self._qle_hd_critical_dist = QLineEdit("0.05")
        self._qle_hd_max_dist = QLineEdit("0.1")

        # other object
        qpb_save = QPushButton("Save")
        qpb_save.clicked.connect(self.slot_save_config)

        # general
        qgb_ss = QGroupBox("Generate ScreenShot Settings")
        qgl_ss = QGridLayout()
        qgl_ss.addWidget(QLabel("ScreenShot Width"))
        qgl_ss.addWidget(self._qle_view_width)
        qgl_ss.addWidget(QLabel("ScreenShot Height"))
        qgl_ss.addWidget(self._qle_view_height)
        qgl_ss.addWidget(self._qcb_force_update)
        qgl_ss.addWidget(self._qcb_specular)
        qgl_ss.addWidget(self._qcb_enable_color)
        qgl_ss.addWidget(self._qcb_enable_texture)
        qgl_ss.addWidget(self._qcb_trans_bd)
        qgb_ss.setLayout(qgl_ss)
        # hausdorff doc
        qgb_hd = QGroupBox("Hausdorff Distance Report Configuration")
        qgl_hd = QGridLayout()

        qgl_hd.addWidget(self._qcb_hd_6_sigma)
        qgl_hd.addWidget(QLabel("Legend Direction"))
        qgl_hd.addWidget(self._qcb_hd_legend_type)
        qgl_hd.addWidget(QLabel("Max Nominal Distance"))
        qgl_hd.addWidget(self._qle_hd_nominal_dist)
        qgl_hd.addWidget(QLabel("Max Critical Distance"))
        qgl_hd.addWidget(self._qle_hd_critical_dist)
        qgl_hd.addWidget(QLabel("Max Search Distance"))
        qgl_hd.addWidget(self._qle_hd_max_dist)
        qgb_hd.setLayout(qgl_hd)
        
        qgl_conf = QGridLayout()
        qgl_conf.addWidget(qgb_ss)
        qgl_conf.addWidget(qgb_hd)
        qgl_conf.addWidget(qpb_save)
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
        cfg_obj._config["force_update"] = self._qcb_force_update.isChecked()
        cfg_obj._config["specular"] = self._qcb_specular.isChecked()
        cfg_obj._config["enable_color"] = self._qcb_enable_color.isChecked()
        cfg_obj._config["enable_texture"] = self._qcb_enable_texture.isChecked()
        cfg_obj._config["trans_bd"] = self._qcb_trans_bd.isChecked()
        cfg_obj._config["view_width"] = self._qle_view_width.text()
        cfg_obj._config["view_height"] = self._qle_view_height.text()
        cfg_obj._config["hd_6_sigma"] = self._qcb_hd_6_sigma.isChecked()
        cfg_obj._config["hd_legend_type"] = self._qcb_hd_legend_type.currentText()
        cfg_obj._config["hd_nominal_dist"] = self._qle_hd_nominal_dist.text()
        cfg_obj._config["hd_critical_dist"] = self._qle_hd_critical_dist.text()
        cfg_obj._config["hd_max_dist"] = self._qle_hd_max_dist.text()

    def fill_info(self, cfg_obj):
        self._qcb_force_update.setChecked(cfg_obj._config["force_update"])
        self._qcb_specular.setChecked(cfg_obj._config["specular"])
        self._qcb_enable_color.setChecked(cfg_obj._config["enable_color"])
        self._qcb_enable_texture.setChecked(cfg_obj._config["enable_texture"])
        self._qcb_trans_bd.setChecked(cfg_obj._config["trans_bd"])
        self._qle_view_width.setText(cfg_obj._config["view_width"])
        self._qle_view_height.setText(cfg_obj._config["view_height"])
        self._qcb_hd_6_sigma.setChecked(cfg_obj._config["hd_6_sigma"])
        self._qcb_hd_legend_type.setCurrentText(cfg_obj._config["hd_legend_type"])
        self._qle_hd_nominal_dist.setText(cfg_obj._config["hd_nominal_dist"])
        self._qle_hd_critical_dist.setText(cfg_obj._config["hd_critical_dist"])
        self._qle_hd_max_dist.setText(cfg_obj._config["hd_max_dist"])
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")
    w = GeneralConfigurationUI()
    w.show()
    sys.exit(app.exec_())
