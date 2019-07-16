# -*- coding: utf-8 -*-
## @file project_io.py
## @brief transfer module between project_object and xml
## @author jiayanming

import os.path
import datetime
import xml.etree.ElementTree as ET


class Project:
    def __init__(self, filename=""):
        # xml tree object
        self._tree = None
        # global config
        self._configFile = filename
        self._dirInput = ""
        self._dirOutput = ""
        self._exeDemo = ""
        self._exePV = ""
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

    # load functions
    def load_project(self, filename=""):
        if filename != "":
            self._configFile = filename
        self._tree = ET.parse(self._configFile)
        root = self._tree.getroot()
        # directories
        self._dirInput = root.find("input").attrib["path"]
        self._dirOutput = root.find("output").attrib["path"]
        self._exeDemo = root.find("exe_demo").attrib["path"]
        self._exePV = root.find("exe_pv").attrib["path"]
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

    # save functions
    def save_list(self):
        ele_all = ET.Element("all")
        ele_case = ET.Element("case")
        ele_ver = ET.Element("version")
        ele_alg = ET.Element("algorithm")
        for item in self._case:
            ele_case.append(ET.Element("item", {"name":item, "check":"1"}))
        for item in self._alg:
            ele_alg.append(ET.Element("item", {"name":item, "check":"1"}))
        for item in self._ver:
            ele_ver.append(ET.Element("item", {"name":item, "check":"1"}))
        ele_all.append(ele_case)
        ele_all.append(ele_ver)
        ele_all.append(ele_alg)
        return ele_all
        
    def save_check(self, name, cd, ad, vd):
        ele = ET.Element(name)
        ele_case = ET.Element("case")
        ele_ver = ET.Element("version")
        ele_alg = ET.Element("algorithm")
        for item in self._case:
            if item in cd:
                ele_case.append(ET.Element("item", {"name":item, "check":"1"}))
            else:
                ele_case.append(ET.Element("item", {"name":item, "check":"0"}))
        for item in self._alg:
            if item in ad:
                ele_alg.append(ET.Element("item", {"name":item, "check":"1"}))
            else:
                ele_alg.append(ET.Element("item", {"name":item, "check":"0"}))
        for item in self._ver:
            if item in vd:
                ele_ver.append(ET.Element("item", {"name":item, "check":"1"}))
            else:
                ele_ver.append(ET.Element("item", {"name":item, "check":"1"}))
        ele.append(ele_case)
        ele.append(ele_ver)
        ele.append(ele_alg)
        return ele

    def save_project(self, filename=""):
        root = ET.Element("project")
        # directories
        root.append(ET.Element("input", {"path":self._dirInput}))
        root.append(ET.Element("output", {"path":self._dirOutput}))
        root.append(ET.Element("exe_demo", {"path":self._exeDemo}))
        root.append(ET.Element("exe_pv", {"path":self._exePV}))
        root.append(self.save_list())
        root.append(self.save_check("screenshot", self._sCaseCheck, self._sAlgCheck, self._sVerCheck))
        root.append(self.save_check("docx", self._dCaseCheck, self._dAlgCheck, self._dVerCheck))
        return ET.ElementTree(root)

    def save_tree(self, filename=""):
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


if __name__ == "__main__":
    p = Project("")
    p.load_project("d:/dev/py_scripts/test_framework/tf_config.xml")
    p.save_project("d:/tmp/test_input.xml")
    tree = p.save_project()
    tree.write("d:/tmp/test_output.xml")
    #p.load_from_fs()
    print(p._case)
