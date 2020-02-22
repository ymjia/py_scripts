import pdb
import re
import os
import sys
import cv2
import math
import openpyxl
import numpy as np
from PIL import Image
from operator import itemgetter




def read_config_list(config_str, pattern):
    lc = len(config_str)
    lp = len(pattern)
    if lc < lp:
        return None
    if config_str[0:lp] != pattern:
        return None
    return config_str[lp+1:].split(" ")


def read_compare_config(file_config):
    if not os.path.exists(file_config):
        return None
    case_list = []
    ver_list = []
    alg_list = []
    content = None
    with open(file_config, encoding='utf-8') as f:
        content = f.readlines()
    print(content)
    str_list = [l.strip() for l in content]
    for line in str_list:
        if line[0:3] == "cas":
            case_list = read_config_list(line, "cas")
        elif line[0:3] == "ver":
            ver_list = read_config_list(line, "ver")
        elif line[0:3] == "alg":
            alg_list = read_config_list(line, "alg")
    return case_list, ver_list, alg_list


def regex_cid(in_str):
    m = re.search('.*([\d]{8}[\d\+/\-]*).*', in_str)
    if m:
        return m.group(1)
    return ""


# sort and itemgetter
# t_list = [(1, 0, 2)]
# t_list.append((1, 3, 4))
# t_list.append((2, 3, 6))
# t_list.append((3, 1, 6))
# t_list.append((4, 3, 8))
# t_list.append((1, 4, 9))
# t_list.append((2, 1, 10))
# t_list.sort(key=itemgetter(0,1))
# print(t_list[0:2])


#image
#img_pil = Image.open("c:/data/xls/check/img_2.png")
img_name = "c:/dev/py_scripts/ai/input/tmp/noise.png"

def get_line_length(l):
    w = abs(l[0][2] - l[0][0]) 
    h = abs(l[0][1] - l[0][3])
    return w * w + h * h


def find_max_line(img_name):
    img_cv = cv2.imread(img_name)
    dst = cv2.Canny(img_cv, 50, 200, 3);
    cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    lines = cv2.HoughLinesP(dst, 1, 3.1415926 / 180, 300, 400, 80)
    if len(lines) < 1:
        return None
    max_l = lines[0]
    max_len = 0
    for l in lines:
        cur_len = get_line_length(l)
        if cur_len > max_len:
            max_l = l
            max_len = cur_len
    cv2.line(cdst, (max_l[0][0], max_l[0][1]), (max_l[0][2], max_l[0][3]), (255, 255, 0), 3, 2)
    Image.fromarray(cdst).save("d:/dev/py_scripts/ai/input/tmp/error_img_line.png")
    return max_l


def rotate_horizontal(img, l):
    r, c = img.shape[:2]
    print(l)
    angle = math.atan((l[0][3] - l[0][1]) / (l[0][2] - l[0][0]))
    angle_d = angle / math.pi * 180
    print(angle_d)
    mat = cv2.getRotationMatrix2D((0, 0), angle_d, 1)
    res = cv2.warpAffine(img, mat, (r, c))
    return res


def denoise_image(img):
    img_bw = 255*(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) > 5).astype('uint8')

    se1 = cv2.getStructuringElement(cv2.MORPH_RECT, (5,5))
    se2 = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    mask = cv2.morphologyEx(img_bw, cv2.MORPH_CLOSE, se1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, se2)
    mask = np.dstack([mask, mask, mask]) / 255
    out = img * mask
    return out


#img = cv2.imread(img_name)

#res = denoise_image(img)
#res = cv2.medianBlur(img, 3)
def denoise_by_components(in_img, min_size):
    img = in_img
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bw = cv2.adaptiveThreshold(cv2.bitwise_not(grey), 255,
                               cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, -2)
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(bw, connectivity=4)
    sizes = stats[1:, -1]
    nb_components = nb_components - 1
    #for every component in the image, you keep it only if it's above min_size
    for i in range(0, nb_components):
        if sizes[i] <= min_size:
            img[output == i + 1] = 255
    return img

#img = denoise_by_components(img, 30)
#cv2.imwrite("c:/tmp/denoise.png", img)

def copy_sheet(path_from, path_to, sheet_name):
    wb_from = openpyxl.load_workbook(path_from) 
    sheet_list = wb_from.sheetnames
    if sheet_name not in sheet_list:
        print("Error! no sheet {} in file {}".format(sheet_name, excel_from))
        return
    ws_from = wb_from[sheet_name]

    wb = openpyxl.load_workbook(path_to)
    try:
        ws = wb[sheet_name]
        wb.remove(ws)
    except KeyError:
        pass
    sheet = wb.create_sheet(title=sheet_name,index=13)

    for rid, r in enumerate(ws_from.iter_rows(values_only=True)):
        for cid, cell_v in enumerate(r):
            sheet.cell(row=rid+1, column=cid+1).data_type = "s"
            sheet.cell(row=rid+1, column=cid+1).value = cell_v
    wb.save(path_to)
    print("{} copyed from {} to {}".format(sheet_name, path_from, path_to))




copy_sheet("d:/tmp/广州第一分公司202001.xlsx", "d:/tmp/tmp_out.xlsx", "TB 202001")
# t_in = openpyxl.load_workbook("d:/tmp/tmp.xlsx")
# t_out = openpyxl.Workbook()
# ws_in = t_in.active
# txt = ws_in.cell(row=1, column = 1).value
# ws_out = t_out.active
# ws_out.cell(row=1, column = 1).data_type = "s"
# ws_out.cell(row=1, column = 1).value = txt
# t_out.save("d:/tmp/tmp_out.xlsx")
