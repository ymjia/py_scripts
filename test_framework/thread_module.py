import subprocess
import os.path

from PyQt5.QtCore import QThread

from test_framework import ui_logic


class ExeRunThread(QThread):
    def __init__(self, w_main):
        QThread.__init__(self)
        self._mainWindow = w_main

    def __del__(self):
        self.wait()

    def run(self):
        p_obj = self._mainWindow._p
        exe = p_obj._exeDemo
        list_case = ui_logic.get_checked_items(p_obj._case, p_obj._eCaseCheck)
        for case in list_case:
            param = ui_logic.generate_exe_param(p_obj, case)
            in_param = param.split(" ")
            in_param.insert(0, exe)
            proc_demo = subprocess.Popen(in_param, cwd=os.path.dirname(exe))
            proc_demo.wait()
        ver = p_obj._eVer
        if ver == "" or ver in p_obj._ver:
            return
        p_obj._ver.append(ver)
        self._mainWindow.fill_ui_info(p_obj)

