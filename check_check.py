# -*- coding: utf-8 -*-
## @file check_check.py
## @brief create diff from given check list file
## @author jiayanming
import os.path
import math
import datetime
from openpyxl import *

from bisect import bisect_left


class check_item:
    def __init__(self, cid, amount, supplier, rid):
        self.check_id = cid
        self.amount = amount
        self.sup = supplier
        self.rid = rid

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.check_id < other.check_id
        return self.check_id < str(other)

    check_id = 0 #use int for fast compare
    amount = 0 
    sup = "" # supplier
    rid = -1


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
    
## @todo return map information
## return ver_ids specify verified item positions in ver_list
def id_group_equal(ver_list, ap_id, amount, ver_ids):
    id_list = []
    id_type = parse_check_id(ap_id, id_list)
    if id_type == 1:
        return False
    if id_type == 2:
        ver_id = binary_search(ver_list, id_list[0])
        if ver_id == -1:
            return False
        elif ver_list[ver_id].amount == amount:
            ver_ids.append(ver_id)
            return True
        else:
            return False
    if id_type == 3:
        #if last_2 equal
        #else use first n-2
        return False
        #find first item
        
    
# column
#          check  amount  sup
# verify :   B      E      H
# input  :   F      M      query in verify
def load_verify_item(filename, ver_list):
    ws = load_workbook(filename).active
    rid = 2
    for r in ws.iter_rows(min_row=2, max_col=8, values_only=True):
        #print("{}:{} {} {}".format(rid, r[1], r[4], r[7]))
        ver_list.append(check_item(r[1], float(r[4]), r[7], rid))
        rid += 1
    ver_list.sort(key=lambda x: x.check_id, reverse=False)




## load ap check items
## @return:
## ap_list varified list
## am_err_list check item found in ver_list but amount not equal
## no_id_list  check_item cannot found in ver_list
## invalid_list check_item with invalid check_id
## @note need ver_list filled first
def load_ap_item(filename, ver_list, ap_list, am_err_list, no_id_list, invalid_list):
    ws = load_workbook(filename).active
    rid = 1
    for r in ws.iter_rows(min_row=2, max_col=13, values_only=True):
        rid += 1
        cid = r[5].replace(" ", "")
        am = float(r[12])
        cur_item = check_item(cid, am, "", rid)
        if len(cid) != 8 or not (cid.isdigit()):
            invalid_list.append(cur_item)
            continue
        ver_pos = binary_search(ver_list, cid)
        if ver_pos == -1:
            no_id_list.append(cur_item)
            continue
        cur_item.sup = ver_list[ver_pos].sup
        if ver_list[ver_pos].amount != am:
            am_err_list.append(cur_item)
            continue
        ap_list.append(cur_item)




    
    
############## start process ########################
# ver_list = []
# load_verify_item("c:/data/xls/verify.xlsx", ver_list)
# ap_list = []
# am_err_list = []
# no_id_list = []
# invalid_list = []
# load_ap_item("c:/data/xls/ap.xlsx", ver_list, ap_list,
#              am_err_list, no_id_list, invalid_list)

# print("valid: {}\n".format(len(ap_list)))
# print("am_err: {}\n".format(len(am_err_list)))
# print("no_id: {}\n".format(len(no_id_list)))
# print("invalid: {}\n".format(len(invalid_list)))
input_str = "12345/34"
input_str2 = "12345-34/567"
file_id = "c:/data/xls/cid_case.txt"
f = open(file_id)
for line in f:
    parsed_list = []
    res = parse_check_id(line.rstrip(), parsed_list)
    print("{} parse res:{}".format(line.rstrip(), res))
    for p in parsed_list:
        print("--{}".format(p))
