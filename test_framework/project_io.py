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
        self._ver = []
        self._tree = None

    def load_project(self, filename = ""):
        if filename != "":
            self._configFile = filename
        self._tree = ET.parse(self._configFile)
        root = self._tree.getroot()
        # directories
        self._dirInput = root.find("input").attrib["dir"]
        self._dirInput = root.find("output").attrib["dir"]
        #case
        for item in root.find("case"):
            self._case.append(item.attrib["name"])
        #algorithm
        for item in root.find("algorithm"):
            self._alg.append(item.attrib["name"])
        #version
        for item in root.find("version"):
            self._ver.append(item.attrib["name"])

p = Project("")
p.load_project("d:/data/test_framwork/management/project1/tf_config.xml")
