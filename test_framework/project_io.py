# -*- coding: utf-8 -*-
## @file project_io.py
## @brief transfer module between project_object and xml
## @author jiayanming

import os.path
import xml.etree.ElementTree as ET

from test_framework import utils


def xml_find_or_def(root, key, attrib_name, default_val):
    try:
        item = root.find(key)
        if item is None:
            return default_val
        if attrib_name not in item.attrib:
            return default_val
        return item.attrib[attrib_name]
    except ET.ParseError:
        return default_val
    

class Project:
    def __init__(self):
        # xml tree object
        self._tree = ET.ElementTree()
        # global config
        self._configFile = ""
        self._dirInput = ""
        self._dirOutput = ""
        self._exeDemo = ""
        self._exePV = ""
        # case name list
        self._case = []
        self._alg = []
        self._ver = ["input"]
        # exe demo
        self._eCaseCheck = {}
        self._exeParam = "{i} {o}"
        self._eVer = ""
        # screen shot
        self._sCaseCheck = {}
        self._sAlgCheck = {}
        self._sVerCheck = {}
        # doc
        self._dCaseCheck = {}
        self._dAlgCheck = {}
        self._dVerCheck = {}
        self._docName = ""
        self._curDocName = ""
        self._curDocType = "Screenshots"

    # load functions
    def load_xml(self, filename):
        if filename != "":
            self._configFile = filename
        self._tree = ET.parse(self._configFile)
        root = self._tree.getroot()
        # directories
        self._dirInput = root.find("input").attrib["path"]
        self._dirOutput = root.find("output").attrib["path"]
        self._exeDemo = root.find("exe_demo").attrib["path"]
        self._exePV = root.find("exe_pv").attrib["path"]
        self.load_list()
        # exe
        root_exe = root.find("exe")
        self._eCaseCheck.clear()
        for item in root_exe.find("case"):
            if item.attrib["check"] == "1":
                self._eCaseCheck[item.attrib["name"]] = 1
        self._eVer = root_exe.find("version").attrib["str"]
        self._exeParam = root_exe.find("param").attrib["str"]
        # screen shots
        root_ss = root.find("screenshot")
        self.load_check(root_ss, self._sCaseCheck, self._sAlgCheck, self._sVerCheck)
        # doc
        root_doc = root.find("docx")
        self.load_check(root_doc, self._dCaseCheck, self._dAlgCheck, self._dVerCheck)
        self._docName = root_doc.find("doc_name").attrib["name"]
        self._curDocName = root_doc.find("current_name").attrib["name"]
        self._curDocType = xml_find_or_def(root_doc,"current_type","name", "Screenshots")

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
        self.save_item_list(ele_case, self._case, cd)
        self.save_item_list(ele_alg, self._alg, ad)
        self.save_item_list(ele_ver, self._ver, vd)
        ele.append(ele_case)
        ele.append(ele_ver)
        ele.append(ele_alg)
        return ele

    def save_item_list(self, root, item_all, item_dict):
        for item in item_all:
            if item in item_dict:
                root.append(ET.Element("item", {"name": item, "check": "1"}))
            else:
                root.append(ET.Element("item", {"name": item, "check": "0"}))

    def collect_xml(self):
        root = ET.Element("project")
        # directories
        root.append(ET.Element("input", {"path": self._dirInput}))
        root.append(ET.Element("output", {"path": self._dirOutput}))
        root.append(ET.Element("exe_demo", {"path": self._exeDemo}))
        root.append(ET.Element("exe_pv", {"path": self._exePV}))
        root.append(self.save_list())
        # exe
        exe_root = ET.Element("exe")
        ele_case = ET.Element("case")
        self.save_item_list(ele_case, self._case, self._eCaseCheck)
        exe_root.append(ele_case)
        exe_root.append(ET.Element("version", {"str": self._eVer}))
        exe_root.append(ET.Element("param", {"str": self._exeParam}))
        # screenshots
        ss_root = self.save_check("screenshot", self._sCaseCheck,
                                  self._sAlgCheck, self._sVerCheck)
        # docx
        doc_root = self.save_check("docx", self._dCaseCheck, self._dAlgCheck,
                                   self._dVerCheck)
        doc_root.append(ET.Element("doc_name", {"name": self._docName}))
        doc_root.append(ET.Element("current_name", {"name": self._curDocName}))
        doc_root.append(ET.Element("current_type", {"name": self._curDocType}))
        root.append(exe_root)
        root.append(ss_root)
        root.append(doc_root)
        return ET.ElementTree(root)

    def save_xml(self, filename=""):
        file_save = self._configFile
        if filename != "":
            file_save = filename
        if file_save == "":
            return
        self._tree = self.collect_xml()
        utils.indent_xml(self._tree.getroot())
        self._tree.write(file_save)

    def load_case_from_fs(self):
        # load cases from input directory
        dir_in = self._dirInput
        return [f for f in os.listdir(dir_in)
                if os.path.isdir(os.path.join(dir_in, f))]
        # load alg and ver from output dir


def get_checked_items(l_all, d_check):
    res = []
    for i in l_all:
        if i in d_check:
            res.append(i)
    return res
