# -*- coding: utf-8 -*-
## @file project_io.py
## @brief load/save/generate project configration files
## @author jiayanming

import os.path
import math
import datetime
import xml.etree.ElementTree as ET


class Project:
    def __init__(self, filename):
        self._configFile = filename
        self._dirInput = ""
        self._dirOutput = ""
        self._case = []
        self._alg = []
        self.ver = []
        self._tree = None

    def load_project(self, filename = ""):
        if filename != "":
            self._configFile = filename
        self._tree = ET.parse(self._configFile)
        root = self._tree.getroot()
        proj_input = root.find("input")
        print(proj_input.tag)
        print(proj_input.attrib)
        self._dirInput = root.find("input")
    


p = Project("")
p.load_project("d:/data/test_framwork/management/project1/tf_config.xml")
