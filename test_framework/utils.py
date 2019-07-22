# -*- coding: utf-8 -*-
## @file utils.py
## @brief basic run modules for test framework
## @author jiayanming

import os.path
import math
import datetime
from openpyxl import *


def parse_time(time_str):
    tuple = time_str.split(" ")
    return tuple[0], float(tuple[1])


# timming table
# read timming info from output/case/version/
def get_table(dir_o, case, ver):
    times = {}
    file_time = os.path.join(dir_o, case, ver, "timmings.txt")
    if not os.path.exists(file_time):
        message("{} does not exist".format(file_time))
        return None
    with open(file_time) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content if len(l) > 4]
    for line in str_list:
        name, t = parse_time(line)
        times[name] = t
    return times


# generate xlsx table file
def get_compare_table(dir_out, l_case, l_ver, l_alg, file_out):
    wb = Workbook()
    ws = wb.active
    # | alg | case     |    case2   |
    # |     | v1  | v2 |  v1 |  v2  |
    # |alg1 | 0.1 | 0.2|  0.2| 0.3  |
    case_num = len(l_case)
    ver_num = len(l_ver)
    alg_num = len(l_alg)
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
    for i in range(0, alg_num):
        ws.cell(row=i + 3, column=1).value = l_alg[i]
    # table data
    d_case = {}
    d_ver = {}
    d_alg = {}
    for i in range(0, len(l_case)):
        d_case[l_case[i]] = i
    for i in range(0, len(l_ver)):
        d_ver[l_ver[i]] = i
    for i in range(0, len(l_alg)):
        d_alg[l_alg[i]] = i

    def get_pos(case, ver, alg):
        if case not in d_case or ver not in d_ver or alg not in d_alg:
            return -1, -1
        row = d_alg[alg] + 3
        cid = d_case[case]
        vid = d_ver[ver]
        col = ver_num * cid + vid + 2
        return row, col

    for case in l_case:
        for ver in l_ver:
            t_alg = get_table(dir_out, case, ver)
            for alg in l_alg:
                if alg not in t_alg:
                    continue
                r, c = get_pos(case, ver, alg)
                if r == -1 or c == -1:
                    continue
                ws.cell(row=r, column=c).value = t_alg[alg]
    wb.save(file_out)


if __name__ == "__main__":
    file_out = "c:/tmp/time.xlsx"
    l_case = ["case1", "case2"]
    l_ver = ["v11", "v12"]
    l_alg = ["merge", "smooth"]
    dir_out = "c:/data/test_framework/management/project1/output/"
    get_compare_table(dir_out, l_case, l_ver, l_alg, file_out)
