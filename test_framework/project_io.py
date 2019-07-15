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
        # xml tree object
        self._tree = None
        # global config
        self._configFile = filename
        self._dirInput = ""
        self._dirOutput = ""
        # all target list
        self._case = []
        self._alg = []
        self._ver = []
        # all avaliable list
        self._caseList = []
        self._algList = []
        self._verList = []


    def load_project(self, filename = ""):
        if filename != "":
            self._configFile = filename
        self._tree = ET.parse(self._configFile)
        root = self._tree.getroot()
        # directories
        self._dirInput = root.find("input").attrib["dir"]
        self._dirOutput = root.find("output").attrib["dir"]
        #case
        for item in root.find("case"):
            self._case.append(item.attrib["name"])
        #algorithm
        for item in root.find("algorithm"):
            self._alg.append(item.attrib["name"])
        #version
        for item in root.find("version"):
            self._ver.append(item.attrib["name"])


    def save_project(self, filename = ""):
        file_save = self._configFile
        if filename != "":
            file_save = filename
        self._tree.write(file_save)


    def load_from_fs(self):
        # load cases from input directory
        dir_in = self._dirInput
        self._caseList = [f for f in os.listdir(dir_in)
                          if os.path.isdir(os.path.join(dir_in, f))]
        # load alg and ver from output dir


# p = Project("")

# p.load_project("c:/data/test_framwork/management/project1/tf_config.xml")
# p.load_from_fs()

# print(p._case)
# print(p._ver)
# print(p._alg)
# print(p._dirInput)
# print(p._caseList)
