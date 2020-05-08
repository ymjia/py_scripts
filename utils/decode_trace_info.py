# -*- coding: utf-8 -*-
## @file decode_trace_info.py
## @brief get algorithm name\parameter\sequence info from trace
## @author jiayanming

import re
import os.path
import sys

class AlgorithmInfo:
    def __init__(self, name):
        self._name = name
        self._param = []
        self._counter = 1

    def print_self(self):
        print("{} ({})".format(self._name, self._counter))
        for p in self._param:
            print(p)


def find_next_start(lines, idx):
    res_idx = -1
    alg_name = ""
    for i in range(idx, len(lines)):
        line = lines[i]
        if len(line) < 20:
            continue
        if line[0:4] != '====' or line[-4:] != '====':
            continue
        end_idx = line.rfind("parameters")
        start_idx = line.rfind("===", 0, end_idx)
        if end_idx < 1 or start_idx == -1:
            continue
        alg_name = line[start_idx + 3:end_idx - 1]
        res_idx = i
        break
    return alg_name, res_idx


# check if all char in s equal to c
def str_all_equal(s, c):
    for ci in s:
        if ci != c:
            return False
    return True


def find_next_end(lines, idx):
    for i in range(idx, len(lines)):
        if str_all_equal(lines[i], "="):
            return i
    return -1


# delete v/f number from line
def regulate_line(line):
    res = line
    v_idx = res.rfind("with V:")
    if v_idx != -1:
        res = res[0:v_idx]
    vec_idx = res.rfind("std::vector")
    if vec_idx != -1:
        res = res[0:vec_idx + 11]
    return res


skip_alg = ["regmgr_pair_registration", "send_rangeData"]

def decode_alg(f_name):
    res = []
    alg_dict = {} # map from alg_name to alg pos list
    if not os.path.exists(f_name):
        return None
    lines = []
    with open(f_name) as f:
        lines = [l.rstrip() for l in f.readlines()] # only strip end of line
    idx = 0
    while idx < len(lines) and idx != -1:
        alg_name, start_idx = find_next_start(lines, idx)
        if start_idx == -1:
            break
        end_idx = find_next_end(lines, start_idx)
        if end_idx == -1 or end_idx - start_idx < 1:
            break
        # valid alg found
        params = [regulate_line(l) for l in lines[start_idx + 1:end_idx]]
        has_alg = alg_name in alg_dict
        need_add = True
        if has_alg:
            pos_list = alg_dict[alg_name]
            for p in pos_list:
                if alg_name in skip_alg:
                    res[p]._counter += 1
                    need_add = False
                    break
                if res[p]._param == params:
                    res[p]._counter += 1
                    need_add = False
                    break
        if need_add:
            alg = AlgorithmInfo(alg_name)
            alg._param = params
            add_pos = len(res)
            res.append(alg)
            if has_alg:
                alg_dict[alg_name].append(add_pos)
            else:
                alg_dict[alg_name] = [add_pos]
        idx = end_idx + 1
    return res


if __name__ == "__main__":
    filename = sys.argv[1]
    alg_list = decode_alg(filename)
    for a in alg_list:
        a.print_self()
