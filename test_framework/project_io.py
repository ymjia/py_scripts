# -*- coding: utf-8 -*-
## @file project_io.py
## @brief load/save/generate project configration files
## @author jiayanming

import os.path
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
        # case name list
        self._case = []
        self._alg = []
        self._ver = []
        # case dict from name to position
        self._dict_case = {}
        self._dict_alg = {}
        self._dict_ver = {}
        # screen shot
        self._sCaseCheck = []
        self._sAlgCheck = []
        self._sVerCheck = []
        # doc
        self._dCaseCheck = []
        self._dAlgCheck = []
        self._dVerCheck = []

    def load_project(self, filename=""):
        if filename != "":
            self._configFile = filename
        self._tree = ET.parse(self._configFile)
        root = self._tree.getroot()
        # directories
        self._dirInput = root.find("input").attrib["dir"]
        self._dirOutput = root.find("output").attrib["dir"]
        root_ss = root.find("screenshot")
        root_doc = root.find("docx")
        self.load_list()
        self.load_check(root_ss, self._sCaseCheck, self._sAlgCheck, self._sVerCheck)
        self.load_check(root_doc, self._dCaseCheck, self._dAlgCheck, self._dVerCheck)

    def load_list(self):
        branch = self._tree.getroot().find("all")
        self._case.clear()
        for item in branch.find("case"):
            name = item.attrib["name"]
            self._case.append(name)
            self._dict_case[name] = len(self._case)
        # algorithm
        self._alg.clear()
        for item in branch.find("algorithm"):
            self._alg.append(item.attrib["name"])
            self._dict_alg[name] = len(self._alg)
        # version
        self._ver.clear()
        for item in branch.find("version"):
            self._ver.append(item.attrib["name"])
            self._dict_ver[name] = len(self._ver)

    def load_check(self, branch, cc, ac, vc):
        # case
        cc.clear()
        cc.resize(len(self._case))
        for item in branch.find("case"):
            name = item.attrib["name"]
            if name not in self._dict_case:
                continue
            cc[self._dict_case[name]] = int(item.attrib["check"])
        # algorithm
        ac.clear()
        ac.resize(len(self._alg))
        for item in branch.find("algorithm"):
            name = item.attrib["name"]
            if name not in self._dict_alg:
                continue
            ac[self._dict_alg[name]] = int(item.attrib["check"])
        # version
        vc.clear()
        vc.resize(len(self._ver))
        for item in branch.find("version"):
            name = item.attrib["name"]
            if name not in self._dict_ver:
                continue
            vc[self._dict_ver[name]] = int(item.attrib["check"])

    def save_project(self, filename=""):
        file_save = self._configFile
        if filename != "":
            file_save = filename
        self._tree.write(file_save)

    def load_from_fs(self):
        # load cases from input directory
        dir_in = self._dirInput
        return [f for f in os.listdir(dir_in)
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
