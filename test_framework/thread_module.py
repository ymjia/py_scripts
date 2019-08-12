# -*- coding: utf-8 -*-
## @file thread_module.py
## @brief run exe in different thread
## @author jiayanming


import subprocess
import time
import os.path
import datetime
import sys

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

from test_framework import ui_logic
from test_framework import utils


class ExeRunThread(QThread):
    _sigProgress = pyqtSignal(float)

    def __init__(self, w_main):
        QThread.__init__(self)
        self._mainWindow = w_main
        self._demoProc = None
        self._fLog = None
        self._fSts = None

    def __del__(self):
        self.wait()

    def run(self):
        p_obj = self._mainWindow._p
        exe = p_obj._exeDemo
        ext = os.path.splitext(exe)[1]
        exe_py = ""
        if ext == ".py":
            exe_py = utils.get_py_interpretor()
        # prepare exe parameters
        dir_o = p_obj._dirOutput
        cur_ver = p_obj._eVer
        list_case = ui_logic.get_checked_items(p_obj._case, p_obj._eCaseCheck)
        if len(list_case) < 1:
            QMessageBox.about(self._mainWindow, "Error", "No Case Checked!!")
            return
        pg = 95 / len(list_case)
        cur_pg = 5
        sys_info = utils.get_sys_info()
        for case in list_case:
            self._sigProgress.emit(cur_pg)
            cur_pg += pg
            # write logs
            dir_log = os.path.join(dir_o, case, cur_ver, "logs")
            if not os.path.exists(dir_log):
                os.makedirs(dir_log)
            st = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
            file_log = os.path.join(dir_log, "tfl_{}.log".format(st))
            file_sts = os.path.join(dir_log, "tfl_{}.sts".format(st))
            try:
                self._fLog = open(file_log, "w")
                self._fSts = open(file_sts, "a")
                # write machine info
                for line in sys_info:
                    self._fSts.write(line)
            except IOError:
                self._fLog = None
                self._fSts = None
                print("Warning! Fail to open log file {}".format(file_log))
            # run demo
            param = ui_logic.generate_exe_param(p_obj, case)
            in_param = param.split(" ")
            in_param.insert(0, exe)
            if ext == ".py":
                in_param.insert(0, exe_py)
            self._demoProc = utils.ProcessMonitor(in_param, self._fLog)
            try:
                run_st = self._demoProc.execute()
                if not run_st: # return when executable face error
                    continue
                self._demoProc.monite_execution()
                for line in iter(self._demoProc.p.stdout.readline, b''):
                    lined = line.decode('utf-8')
                    sys.stdout.write(lined)
                    self._fLog.write(lined)
                self._demoProc.p.wait()
            finally:
                self._demoProc.close()
            if self._fSts is not None:
                self._fSts.write('Time {0:.2f}\n'.format(self._demoProc.t1 - self._demoProc.t0))
                self._fSts.write('Max_p_mem {0:.2f}MB\n'.format(self._demoProc.max_pmem / 1e6))
                self._fSts.write('Max_v_mem {0:.2f}MB\n'.format(self._demoProc.max_vmem / 1e6))
            self.release_files()
        self._sigProgress.emit(99)
        ver = p_obj._eVer
        if ver != "" and ver not in p_obj._ver:
            p_obj._ver.append(ver)
            self._mainWindow.fill_ui_info(p_obj)

    def release_files(self):
        if self._fLog is not None:
            if not self._fLog.closed:
                self._fLog.close()
            self._fLog = None
        if self._fSts is not None:
            if not self._fSts.closed:
                self._fSts.close()
            self._fSts = None

    def closeEvent(self):
        self._sigProgress.cancel()
