# -*- coding: utf-8 -*-
## @file utils.py
## @brief basic run modules for test framework
## @author jiayanming

import os.path
import psutil
import time
import subprocess
from openpyxl import Workbook


def parse_time(time_str):
    tuple = time_str.split(" ")
    return tuple[0], float(tuple[1])


# timming table
# read timming info from output/case/version/
def get_table(dir_o, case, ver):
    times = {}
    file_time = os.path.join(dir_o, case, ver, "timmings.txt")
    if not os.path.exists(file_time):
        print("{} does not exist".format(file_time))
        return None
    with open(file_time) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content if len(l) > 4]
    for line in str_list:
        name, t = parse_time(line)
        times[name] = t
    return times


# generate xlsx table file
def get_compare_table(dir_out, l_case, l_ver, file_out):
    wb = Workbook()
    ws = wb.active
    # | alg | case     |    case2   |
    # |     | v1  | v2 |  v1 |  v2  |
    # |alg1 | 0.1 | 0.2|  0.2| 0.3  |
    case_num = len(l_case)
    ver_num = len(l_ver)
    # table title
    title_line = ["Case"]
    ver_line = ["Version"]
    for case in l_case:
        title_line.append(case)
        for i in range(0, ver_num-1):
            title_line.append("")
        for vi in l_ver:
            ver_line.append(vi)
    ws.append(title_line)
    ws.append(ver_line)
    for i in range(0, case_num):
        ws.merge_cells(start_row=1, end_row=1,
                       start_column=i * ver_num + 2,
                       end_column=(i+1) * ver_num + 1)
    # table data
    d_case = {}
    d_ver = {}
    for i in range(0, len(l_case)):
        d_case[l_case[i]] = i
    for i in range(0, len(l_ver)):
        d_ver[l_ver[i]] = i
    # initial quadric item list
    d_alg = {}
    idx_alg = 0
    time_quad = []
    for case in l_case:
        for ver in l_ver:
            t_alg = get_table(dir_out, case, ver)
            if t_alg is None:
                continue
            for alg, t in t_alg.items():
                if alg not in d_alg:
                    d_alg[alg] = idx_alg
                    idx_alg += 1
                time_quad.append([case, ver, alg, t])

    # get cell position for given case,ver,alg
    def get_pos(case, ver, alg):
        if case not in d_case or ver not in d_ver or alg not in d_alg:
            return -1, -1
        row = d_alg[alg] + 3
        cid = d_case[case]
        vid = d_ver[ver]
        col = ver_num * cid + vid + 2
        return row, col
    # fill time data
    for quad in time_quad:
        r, c = get_pos(quad[0], quad[1], quad[2])
        ws.cell(row=r, column=c).value = quad[3]
    # alg name column
    for item in d_alg.items():
        ws.cell(row=item[1] + 3, column=1).value = item[0]
    wb.save(file_out)


support_ext = [".asc", ".rge", ".obj", ".stl", ".ply", ".srge", ".bin"]


def get_file_list(folder):
    res = []
    for name in os.listdir(folder):
        if os.path.isdir(os.path.join(folder, name)):
            continue
        ext = os.path.splitext(name)[1]
        if not any(ext in e for e in support_ext):
            continue
        res.append(os.path.join(folder, name))
    return res


class ProcessMonitor:
    def __init__(self, command):
        self.command = command
        self.execution_state = False

    def execute(self):
        self.max_vms_memory = 0
        self.max_rss_memory = 0
        self.t1 = None
        self.t0 = time.time()
        if len(self.command) < 1:
            return
        dir_exe = os.path.dirname(self.command[0])
        self.p = subprocess.Popen(
            self.command, shell=False, cwd=dir_exe,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.execution_state = True

    def poll(self):
        if not self.check_execution_state():
            return False
        self.t1 = time.time()
        try:
            pp = psutil.Process(self.p.pid)
            # obtain a list of the subprocess and all its descendants
            descendants = list(pp.children(recursive=True))
            descendants = descendants + [pp]

            rss_memory = 0
            vms_memory = 0

            #calculate and sum up the memory of the subprocess and all its descendants 
            for descendant in descendants:
                try:
                    mem_info = descendant.memory_info()
                    rss_memory += mem_info[0]
                    vms_memory += mem_info[1]
                except psutil.NoSuchProcess:
                    #sometimes a subprocess descendant will have terminated between the tim
                    # we obtain a list of descendants, and the time we actually poll this
                    # descendant's memory usage.
                    pass
            self.max_vms_memory = max(self.max_vms_memory, vms_memory)
            self.max_rss_memory = max(self.max_rss_memory, rss_memory)
        except psutil.NoSuchProcess:
            return self.check_execution_state()
        return self.check_execution_state()

    def is_running(self):
        return psutil.pid_exists(self.p.pid) and self.p.poll() is None

    def check_execution_state(self):
        if not self.execution_state:
            return False
        if self.is_running():
            return True
        self.executation_state = False
        self.t1 = time.time()
        return False

    def close(self, kill=False):
        try:
            pp = psutil.Process(self.p.pid)
            if kill:
                pp.kill()
            else:
                pp.terminate()
        except psutil.NoSuchProcess:
            pass


if __name__ == "__main__":
    # I am executing "make target" here
    test_exe = "C:/data/send/autoscan_socket/tools/JYMTest/JYMTest.exe"
    param = "-a io -i c:/data/test_framework/management/project1/input/case1/old_3M.ply -o c:/data/test_framework/management/project1/output/case1/test/test"
    p_list = param.split(" ")
    p_list.insert(0, test_exe)
    ptimer = ProcessMonitor(p_list)
    try:
        ptimer.execute()
        # poll as often as possible; otherwise the subprocess might 
        # "sneak" in some extra memory usage while you aren't looking
        while ptimer.poll():
            time.sleep(.5)
    finally:
        # make sure that we don't leave the process dangling?
        ptimer.close()

    print('return code: {}'.format(ptimer.p.returncode))
    print('time: {}'.format(ptimer.t1 - ptimer.t0))
    print('max_vms_memory: {}'.format(ptimer.max_vms_memory))
    print('max_rss_memory: {}'.format(ptimer.max_rss_memory))
    # file_out = "c:/tmp/time.xlsx"
    # l_case = ["case1", "case2"]
    # l_ver = ["v11", "v12"]
    # #l_alg = ["merge", "smooth"]
    # dir_out = "c:/data/test_framework/management/project1/output/"
    # get_compare_table(dir_out, l_case, l_ver, file_out)
