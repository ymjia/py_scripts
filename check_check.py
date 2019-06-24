# -*- coding: utf-8 -*-
## @file check_check.py
## @brief create diff from given check list file
## @author jiayanming
import os.path
import math
import datetime
from openpyxl import *


class check_item:
    check_id = 0 #use int for fast compare
    amount = 0 
    sup = "" # supplier
    rid = -1

# column
#          check  amount  sup
# verify :   B      E      G/H
# input  :   F     K/M      B
    
def load_item(wb, item_list):
    for row in ws.values:
        for value in row:
            print(value)

wb = load_workbook(filename='empty_book.xlsx')

ranges = wb['range names']
print(sheet_ranges['D18'].value)
