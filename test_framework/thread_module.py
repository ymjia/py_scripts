# -*- coding: utf-8 -*-
## @file thread_module.py
## @brief run exe in different thread
## @author jiayanming


import subprocess
import time
import os.path
import datetime
import sys
import locale # get subprocess encoding
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal

from test_framework import ui_logic
from test_framework import utils


class ExeRunThread(QThread):
    _sigProgress = pyqtSignal(float) # signal connect to mainwindow progress bar

    def __init__(self, p_obj):
        QThread.__init__(self)
        self.session = p_obj
        self._demoProc = None
        self._fLog = None
        self._fSts = None
        self._fSmp = None

    def __del__(self):
        self.wait()

    def run(self):
        exe = self.session._exeDemo
        # prepare exe parameters
        dir_i = self.session._dirInput
        dir_o = self.session._dirOutput
        cur_ver = self.session._eVer
        cur_cmd = self.session._exeParam
        list_case = ui_logic.get_checked_items(self.session._case, self.session._eCaseCheck)
        self.run_task(exe, cur_cmd, cur_ver, list_case, dir_i, dir_o)

    # run single task, Parallel not supported
    def run_task(self, exe, cmd, ver, l_case, dir_i, dir_o):
        ext = os.path.splitext(exe)[1]
        exe_py = ""
        if ext == ".py":
            exe_py = utils.get_py_interpretor()
        pg = 95 / len(l_case)
        cur_pg = 5
        sys_info = utils.get_sys_info()
        encoding = locale.getpreferredencoding()
        for case in l_case:
            print("## Start {} =====================".format(case))
            self._sigProgress.emit(cur_pg)
            cur_pg += pg
            # write logs
            dir_log = os.path.join(dir_o, case, ver, "logs")
            if not os.path.exists(dir_log):
                os.makedirs(dir_log)
            st = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
            file_log = os.path.join(dir_log, "tfl_{}.log".format(st))
            file_sts = os.path.join(dir_log, "tfl_{}.sts".format(st))
            file_smp = os.path.join(dir_log, "tfl_{}.smp".format(st))
            try:
                self._fLog = open(file_log, "w", encoding="utf-8")
                self._fSts = open(file_sts, "a", encoding="utf-8")
                self._fSmp = open(file_smp, "a", encoding="utf-8")
                # write machine info
                for line in sys_info:
                    self._fSts.write(line)
            except IOError:
                self._fLog = None
                self._fSts = None
                self._fSmp = None
                print("Warning! Fail to open log file {}".format(file_log))
            # run demo and collect proc info
            param = ui_logic.generate_exe_param(dir_i, dir_o, case, exe, cmd, ver)
            in_param = param.split(" ")
            in_param.insert(0, exe)
            if ext == ".py":
                in_param.insert(0, exe_py)
            #TODO change registry table
            self._demoProc = utils.ProcessMonitor(in_param, self._fLog)
            try:
                run_st = self._demoProc.execute()
                if not run_st: # return when executable face error
                    continue
                self._demoProc.monite_execution()
                for line in iter(self._demoProc.p.stdout.readline, b''):
                    lined = line.decode(encoding, errors="ignore")
                    sys.stdout.write(lined)
                    self._fLog.write(lined)
                self._demoProc.p.wait()
            finally:
                self._demoProc.close()
            # write proc memmory information to xls
            if self._fSts is not None:
                self._fSts.write('Time {0:.2f}\n'.format(self._demoProc.t1 - self._demoProc.t0))
                self._fSts.write('Max_p_mem {0:.2f}MB\n'.format(self._demoProc.max_pmem / 1e6))
                self._fSts.write('Max_v_mem {0:.2f}MB\n'.format(self._demoProc.max_vmem / 1e6))
            if self._fSmp is not None:
                for li in range(0, len(self._demoProc._cpuSample)):
                    res_str = "{0:.2f} {1:.2f}\n".format(
                        self._demoProc._cpuSample[li],
                        self._demoProc._memSample[li])
                    self._fSmp.write(res_str)
            self.release_files()
            print("## Finished {} =====================".format(case))
        self._sigProgress.emit(99)

    def release_files(self):
        if self._fLog is not None:
            if not self._fLog.closed:
                self._fLog.close()
            self._fLog = None
        if self._fSts is not None:
            if not self._fSts.closed:
                self._fSts.close()
            self._fSts = None
        if self._fSmp is not None:
            if not self._fSmp.closed:
                self._fSmp.close()
            self._fSmp = None

    def closeEvent(self):
        self._sigProgress.cancel()
