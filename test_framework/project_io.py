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
        # screen shot
        self._sCaseCheck = {}
        self._sAlgCheck = {}
        self._sVerCheck = {}
        # doc
        self._dCaseCheck = {}
        self._dAlgCheck = {}
        self._dVerCheck = {}

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
        # algorithm
        self._alg.clear()
        for item in branch.find("algorithm"):
            self._alg.append(item.attrib["name"])
        # version
        self._ver.clear()
        for item in branch.find("version"):
            self._ver.append(item.attrib["name"])

    def load_check(self, branch, cd, ad, vd):
        # case
        cd.clear()
        for item in branch.find("case"):
            if item.attrib["check"] == "1":
                cd[item.attrib["name"]] = 1
        # algorithm
        ad.clear()
        for item in branch.find("algorithm"):
            if item.attrib["check"] == "1":
                ad[item.attrib["name"]] = 1
        # version
        vd.clear()
        for item in branch.find("version"):
            if item.attrib["check"] == "1":
                vd[item.attrib["name"]] = 1

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


def get_checked_items(l_all, d_check):
    res = []
    for i in l_all:
        if i in d_check:
            res.append(l_all[i])
    return res


# p = Project("")

# p.load_project("c:/data/test_framwork/management/project1/tf_config.xml")
# p.load_from_fs()

# print(p._case)
# print(p._ver)
# print(p._alg)
# print(p._dirInput)
# print(p._caseList)
