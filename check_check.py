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
        cid = r[5]
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
    
ver_list = []
load_verify_item("c:/data/xls/verify.xlsx", ver_list)
ap_list = []
am_err_list = []
no_id_list = []
invalid_list = []
load_ap_item("c:/data/xls/ap.xlsx", ver_list, ap_list,
             am_err_list, no_id_list, invalid_list)

print("valid: {}\n".format(len(ap_list)))
print("am_err: {}\n".format(len(am_err_list)))
print("no_id: {}\n".format(len(no_id_list)))
print("invalid: {}\n".format(len(invalid_list)))
