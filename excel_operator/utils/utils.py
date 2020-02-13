# -*- coding: utf-8 -*-
## @file check_check.py
## @brief create diff from given check list file
## @author jiayanming
import pdb
import os.path
import sys
import re
import math
from openpyxl import *

filename = ""
cwd = os.getcwd()
dir_input = os.fsencode(os.path.join(cwd, "input"))


#### load file
table = load_workbook(filename)
ws = table.active

## constant
idx_avalible = 5
idx_hz = 11
idx_health = 18
idx_dep = 4

dep_name_list = [
    "董事会办公室",
    "财务部","国际事业部",
"知识产权法务部", 
"科技发展部", 
"行政部", 
"人力资源部", 
"信息技术部", 
"品质部", 
"采购物流部", 
"生产部", 
"杭州研究院", 
"研发管理部", 
"基础软件研发部", 
"基础硬件研发部", 
"测试部", 
"3D打印研发部", 
"3D数字化研发部", 
"齿科数字化研发部", 
"销售管理部", 
"市场部", 
"齿科数字化事业部", 
"3D数字化渠道部", 
"3D鞋数字化产品部", 
"审计部", 
"数字系统"]
class depart:
    def __init__(self, name):
        self.dep_name = name
        self.total = 0
        self.hz = 0
        self.hz_r = 0
        self.hz_y = 0
        self.hz_g = 0
        self.hz_n = 0
        self.nhz = 0
        self.nhz_r = 0
        self.nhz_y = 0
        self.nhz_g = 0
        self.nhz_n = 0
        self.nodata = 0

def my_decode(org):
    #return bytes(org, 'utf-8-sig').decode("gbk","ignore")
    #return org.encode('gbk').decode("utf-8", 'ignore')
    return org

dep_map = {}
dep_list = []
#### read lines
rows =  ws.iter_rows(min_row=2, max_col=20, values_only=True)
rid = 0
for r in rows:
    rid += 1
    tmp_dep = my_decode(r[idx_dep])
    dep = ""
    dep_pos = 1000
    for dn in dep_name_list:
        cur_pos = tmp_dep.find(dn)
        if cur_pos == -1 or cur_pos > dep_pos:
            continue
        dep = dn
        dep_pos = cur_pos
    if dep == "":
        print("warning! cannot find dep for line{}".format(rid))
    nodata = my_decode(r[idx_avalible]) == my_decode("否")
    hz_str = my_decode(r[idx_hz])
    hz = hz_str  == my_decode("已返回")
    health = my_decode(r[idx_health])

    cur_dep = None
    if dep in dep_map:
        cur_dep = dep_list[dep_map[dep]]
    else:
        tmp_id = len(dep_list)
        dep_map[dep] = tmp_id
        dep_list.append(depart(dep))
        cur_dep = dep_list[tmp_id]
    cur_dep.total += 1
    if nodata:
        cur_dep.nodata += 1
        continue
    if hz:
        cur_dep.hz += 1
        if health == my_decode("绿色"):
            cur_dep.hz_g += 1
        elif health == my_decode("黄色"):
            cur_dep.hz_y += 1
        elif health == my_decode("红色"):
            cur_dep.hz_r += 1
        else:
            cur_dep.hz_n += 1
    else:
        cur_dep.nhz += 1
        if health == my_decode("绿色"):
            cur_dep.nhz_g += 1
        elif health == my_decode("黄色"):
            cur_dep.nhz_y += 1
        elif health == my_decode("红色"):
            cur_dep.nhz_r += 1
        else:
            cur_dep.nhz_n += 1
### read all tables


wb = Workbook()
ws = wb.active
ws.append(["部门", "总数A", "未填写", "在杭B", "在杭绿码C", "在杭黄码D", "在杭红码E", "未申请码X", "未回杭F", "未回杭绿码G", "回杭黄码H", "未回杭红码I", "未回未申请码Y"])
for dep in dep_list:
    ws.append([
        dep.dep_name,
        dep.total,
        dep.nodata,
        dep.hz,
        dep.hz_g,
        dep.hz_y,
        dep.hz_r,
        dep.hz_n,
        dep.nhz,
        dep.nhz_g,
        dep.nhz_y,
        dep.nhz_r,
        dep.nhz_n
        ])
wb.save("c:/tmp/output.xlsx")
