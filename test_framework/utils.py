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


if __name__ == "__main__":
    file_out = "c:/tmp/time.xlsx"
    l_case = ["case1", "case2"]
    l_ver = ["v11", "v12"]
    #l_alg = ["merge", "smooth"]
    dir_out = "c:/data/test_framework/management/project1/output/"
    get_compare_table(dir_out, l_case, l_ver, file_out)
