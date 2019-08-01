import subprocess
import os.path

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

from test_framework import ui_logic


class ExeRunThread(QThread):
    _sigProgress = pyqtSignal(float)

    def __init__(self, w_main):
        QThread.__init__(self)
        self._mainWindow = w_main

    def __del__(self):
        self.wait()

    def run(self):
        p_obj = self._mainWindow._p
        exe = p_obj._exeDemo
        list_case = ui_logic.get_checked_items(p_obj._case, p_obj._eCaseCheck)
        if len(list_case) < 1:
            QMessageBox.about(self._mainWindow, "Error", "No Case Checked!!")
            return
        pg = float(1) / len(list_case)
        cur_pg = 0
        for case in list_case:
            self.sleep(2)
            cur_pg += pg
            self._sigProgress.emit(cur_pg)
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
