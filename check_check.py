# -*- coding: utf-8 -*-
## @file check_check.py
## @brief create diff from given check list file
## @author jiayanming
import os.path
import math
import datetime
from openpyxl import *

from bisect import bisect_left

ver_map = {}
ap_map = {}

class CheckItem:
    def __init__(self, cid, amount, supplier, rid):
        self.check_id = cid
        self.amount = amount
        self.sup = supplier
        self.rid = rid
        self.map_id = -1

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.check_id < other.check_id
        return self.check_id < str(other)

    check_id = 0 #use int for fast compare
    amount = 0 
    sup = "" # supplier
    rid = -1
    dup_list = []
    map_id = -1
    


def binary_search(a, x, lo=0, hi=None):
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)
    return (pos if pos != hi and a[pos].check_id == x else -1)


def merge_str(long_str, short_str):
    len_s = len(long_str) - len(short_str)
    return long_str[0:len_s] + short_str


## find previous number from given start position
def find_prev_number(input_str, pos):
    idx = pos - 1
    while idx >= 0 and input_str[idx].isdigit():
        idx -= 1
    return input_str[idx+1:pos]


## find next number from given start position
def find_next_number(input_str, pos):
    max_pos = len(input_str)
    idx = pos + 1
    while idx < max_pos and input_str[idx].isdigit():
        idx += 1
    return input_str[pos+1:idx]

## parse id list from compound str
## @return
## 0 normal finish
## 1 prefix invalid
## 2 prefix valid & no valid number following
## 3 ambiguous parse
def parse_check_id(input_id, out_list=[]):
    out_list.clear()
    if len(input_id) <= 8:
        return
    prefix = input_id[0:8]
    #lenth judge for short ids
    if not prefix.isdigit():
        return 1
    next_number = find_next_number(input_id, 8)
    len_next = len(next_number)
    if len_next == 0 or len_next >= 8:
        out_list.append(prefix)
        return 2 # cannot find next number
    prev_number = prefix[8 - len_next:]
    if input_id[8] == "-":
        start = int(prev_number)
        end = int(next_number)
        for i in range(start, end + 1):
            out_list.append(merge_str(prefix, str(i)))
        if len_next + 9 >= len(input_id):
            out_list.append(prefix)
            out_list.append(merge_str(prefix, next_number))
            return 3
    else:
        out_list.append(merge_str(prefix, prev_number))
        out_list.append(merge_str(prefix, next_number))
    # add other check
    split_pos = 8
    while True:
        split_pos = split_pos + len_next + 1
        if split_pos >= len(input_id):
            break
        next_number = find_next_number(input_id, split_pos)
        len_next = len(next_number)
        out_list.append(merge_str(prefix, next_number))
    return 0


def amount_equal(ver_list, ap_item, cid_list):
    ap_rid = ap_item.rid
    ap_am = ap_item.amount
    ver_ids = []
    ver_am = 0
    sup = ["JYM"]
    for i in cid_list:
        if i not in ver_map:
            return False
        tmp_find = ver_map[i]
        ver_ids.append(tmp_find)
        ver_item = ver_list[tmp_find]
        ver_am += ver_item.amount
        if sup[0] != "JYM" and sup[0] != ver_item.sup:
            print("ERROR! sup in ap table line {}".format(ap_rid))
        sup[0] = ver_item.sup
    ap_item.sup = sup[0]
    if not math.isclose(ap_am, ver_am, abs_tol=1e-5):
        return False
    # record map information
    ap_item.map_id = 0
    if len(ver_ids) == 1:
        ap_item.map_id = ver_list[ver_ids[0]].rid
    for i in ver_ids:
        ver_list[i].map_id = ap_rid
    return True


## @todo return map information
## return ver_ids specify verified item positions in ver_list
def id_group_equal(ver_list, ap_item):
    id_list = []
    id_type = parse_check_id(ap_item.check_id, id_list)
    if id_type == 0:
        return amount_equal(ver_list, ap_item, id_list)
    if id_type == 1:
        return False
    if id_type == 2:
        return amount_equal(ver_list, ap_item, id_list[0:1])
    if id_type == 3:
        res_p = amount_equal(ver_list, ap_item, id_list[-2:-1])
        if res_p is True:  # if prefix equal
            return True
        res_l2 = amount_equal(ver_list, ap_item, id_list[-1:])
        if res_l2 is True:  # if last 2 equal
            return True
        res_n2 = amount_equal(ver_list, ap_item, id_list[:-2])
        if res_n2 is True:  # if first n-2 equal
            return True
    return False
    
# column
#          check  amount  sup
# verify :   B      E      H
# input  :   F      M      query in verify
def load_verify_item(filename, ver_list):
    ver_map.clear()
    ws = load_workbook(filename).active
    rid = 2
    for r in ws.iter_rows(min_row=2, max_col=8, values_only=True):
        cid = r[1]
        ver_map[cid] = len(ver_list)
        ver_list.append(CheckItem(cid, float(r[4]), r[7], rid))

        rid += 1
    #ver_list.sort(key=lambda x: x.check_id, reverse=False)

# load ap item and remove duplicated
def load_ap_input(filename, ap_input_list):
    ws = load_workbook(filename).active
    rid = 1
    for r in ws.iter_rows(min_row=2, max_col=13, values_only=True):
        rid += 1
        cid = r[5].replace(" ", "")
        am = float(r[12])
        if cid not in ap_map:
            ap_map[cid] = len(ap_input_list)
            ap_input_list.append(CheckItem(cid, am, "", rid))
        else:
            old_pos = ap_map[cid]
            old_item = ap_input_list[old_pos]
            old_item.amount += am
            old_item.dup_list.append(rid)


## load ap check items
## @return:
## ap_list varified list
## am_err_list check item found in ver_list but amount not equal
## no_id_list  check_item cannot found in ver_list
## invalid_list check_item with invalid check_id
## @note need ver_list filled first
def filter_ap_item(ver_list, ap_input_list, ap_list, am_err_list, no_id_list, invalid_list):
    for cur_item in ap_input_list:
        rid = cur_item.rid
        cid = cur_item.check_id
        am = cur_item.amount
        if len(cid) != 8 or not (cid.isdigit()):
            if id_group_equal(ver_list, cur_item):
                ap_list.append(cur_item)
                continue
            else:
                invalid_list.append(cur_item)
                continue
        if cid not in ver_map:
            no_id_list.append(cur_item)
            continue
        ver_pos = ver_map[cid]
        ver_item = ver_list[ver_pos]
        cur_item.sup = ver_item.sup
        if not math.isclose(ver_item.amount, am, abs_tol=1e-5):
            am_err_list.append(cur_item)
            continue
        ver_item.map_id = rid
        cur_item.map_id = ver_item.rid
        #print("v {} - {}".format(ver_item.rid, rid))
        ap_list.append(cur_item)


## debugging methods
def print_ver_number(ver_list, stage):
    verified_number = 0
    for v in ver_list:
        if v.map_id != -1:
            verified_number += 1
    print("verified number at {} : {}".format(stage, verified_number))


############## start process ########################
ver_list = []
ap_input_list = []
ap_list = []
am_err_list = []
no_id_list = []
invalid_list = []

load_verify_item("c:/data/xls/verify.xlsx", ver_list)
load_ap_input("c:/data/xls/ap.xlsx", ap_input_list)
print("ap number after remove dup: {}".format(len(ap_input_list)))
filter_ap_item(ver_list, ap_input_list, ap_list,
               am_err_list, no_id_list, invalid_list)
print("valid: {}\n".format(len(ap_list)))
print("am_err: {}\n".format(len(am_err_list)))
print("no_id: {}\n".format(len(no_id_list)))
print("invalid: {}\n".format(len(invalid_list)))


def write_item_to_file(filename, out_list):
    wb = Workbook()
    ws = wb.active
    ws.append(["check_id", "amount", "row_no", "map_id", "supplier"])
    for vi in out_list:
        ws.append([vi.check_id, vi.amount, vi.rid, vi.map_id, vi.sup])
    wb.save(filename)


write_item_to_file("c:/tmp/ver_test.xlsx", ver_list)
write_item_to_file("c:/tmp/ap_confirm.xlsx", ap_list)
write_item_to_file("c:/tmp/ap_am_err.xlsx", am_err_list)
write_item_to_file("c:/tmp/invalid_id.xlsx", invalid_list)
