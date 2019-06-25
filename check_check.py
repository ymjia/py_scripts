# -*- coding: utf-8 -*-
## @file check_check.py
## @brief create diff from given check list file
## @author jiayanming
import os.path
import math
import datetime
from openpyxl import *


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

# column
#          check  amount  sup
# verify :   B      E      H
# input  :   F      M      query in verify


def load_item(filename, item_list):
    ws = load_workbook(filename).active
    rid = 2
    for r in ws.iter_rows(min_row=2, max_col=8, max_row=5, values_only=True):
        #print("{}:{} {} {}".format(rid, r[1], r[4], r[7]))
        item_list.append(check_item(r[1], float(r[4]), r[7], rid))
        rid += 1
    item_list.sort(key=lambda x: x.check_id, reverse=False)


from bisect import bisect_left

def binary_search(a, x, lo=0, hi=None):
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)
    return (pos if pos != hi and a[pos].check_id == x else -1)


item_list = []
load_item("c:/data/xls/verify.xlsx", item_list)
for i in item_list:
    print("{}:{} {} {}".format(i.rid, i.check_id, i.amount, i.sup))
print(binary_search(item_list, "21320505"))
print(binary_search(item_list, "21320503"))
