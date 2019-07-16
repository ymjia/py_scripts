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
        # screen shot
        self._sCase = []
        self._sAlg = []
        self._sVer = []
        self._sCaseCheck = []
        self._sAlgCheck = []
        self._sVerCheck = []
        # doc
        self._dCase = []
        self._dAlg = []
        self._dVer = []
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
        self.load_list(root_ss, self._sCase, self._sAlg, self._sVer,
                       self._sCaseCheck, self._sAlgCheck, self._sVerCheck)
        self.load_list(root_doc, self._dCase, self._dAlg, self._dVer,
                       self._dCaseCheck, self._dAlgCheck, self._dVerCheck)

    def load_list(self, branch, case, alg, ver, cc, ac, vc):
        # case
        case.clear()
        cc.clear()
        for item in branch.find("case"):
            case.append(item.attrib["name"])
            cc.append(int(item.attrib["check"]))
        # algorithm
        alg.clear()
        ac.clear()
        for item in branch.find("algorithm"):
            alg.append(item.attrib["name"])
            ac.append(int(item.attrib["check"]))
        # version
        ver.clear()
        vc.clear()
        for item in branch.find("version"):
            ver.append(item.attrib["name"])
            vc.append(int(item.attrib["check"]))

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
