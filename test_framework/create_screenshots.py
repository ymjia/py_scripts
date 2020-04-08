# -*- coding: utf-8 -*-
## @file create_screenshots.py
## @brief create screenshots for mesh in given position
## @author jiayanming
import os
import os.path
import sys
import math
import time
import datetime
from shutil import move
from paraview.simple import *
from paraview.simple import _active_objects
from paraview.simple import GetDisplayProperties
dir_py_module = os.path.join(os.getcwd(), "..", "Sn3D_plugins", "scripts", "pv_module")
sys.path.append(dir_py_module)
from framework_util import *

## ====================texture =================================
pxm = servermanager.ProxyManager()

def set_texture(display, name):
    cur_t = display.Texture
    if cur_t is not None:
        return
    if name == "":
        return
    # if loaded
    is_loaded = False
    group = pxm.GetProxiesInGroup('textures')
    for key, t in group.items():
        if key[0] == name:
            is_loaded = True
            cur_t = t
            break
    # load picture as texture
    if not is_loaded:
        np = pxm.NewProxy("textures", "ImageTexture")
        fn = np.GetProperty('FileName')
        fn.SetElement(0, name)
        np.UpdateVTKObjects()
        pxm.RegisterProxy("textures", name, np)
        cur_t = np
    if cur_t is not None:
        display.Representation = 'Surface'
        display.BackfaceRepresentation = 'Surface'
        display.DiffuseColor = [1.0, 1.0, 1.0]
        display.Texture = cur_t


def show_texture(cur_source, cur_view):
    # get mesh file name
    name = ""
    if hasattr(cur_source, 'FileNames') and cur_source.FileNames[0]:
        name = cur_source.FileNames[0]
    if hasattr(cur_source, 'FileName'):
        name = cur_source.FileName

    # set texture picture name
    if name == "":
        return
    ext_list = [".jpg", ".png", ".bmp", ".ppm", ".tiff"]
    stem = os.path.splitext(name)[0]
    ext = ""
    for ei in ext_list:
        if os.path.exists(stem + ei):
            ext = ei
            break
    if ext == "":
        name = ""
    else:
        name = stem + ext

    cur_display = GetDisplayProperties(cur_source, cur_view)
    # set texture
    set_texture(cur_display, name)

## end=================texture =================================

## ===================hausdorff distance ======================
def set_hd_output_display(display, view):
    ColorBy(display, ('POINTS', 'Distance'))
    display.SetScalarBarVisibility(view, True)
    display.MapScalars = 1

def generate_vn(s_in, s_name):
    sd = servermanager.Fetch(s_in)
    if not sd.IsA("vtkPolyData"):
        return s_in
    vn = sd.GetPointData().GetNormals()
    if vn is not None:
        return s_in
    sn = GenerateSurfaceNormals(Input=s_in)
    RenameSource("{}_vn".format(s_name), sn)
    return sn

def show_hausdorff_dist(s_name_list):
    s_num = len(s_name_list)
    if s_num != 2:
        print("Error! 2 source need to be selected, current source:")
        print(s_name_list)
        return (None, None, None, None)
    s_list = []
    for name in s_name_list:
        reader = read_files([name])
        if reader is not None:
            s_list.append(reader)
    if len(s_list) != 2:
        print("2 poly mesh needed, now got {}".format(len(s_list)))
        return (None, None, None, None)
    LoadPlugin("./plugins/Utils/Utils.dll", remote=False, ns=globals())
    # get names
    pxm = servermanager.ProxyManager();
    name0 = os.path.splitext(pxm.GetProxyName("sources", s_list[0]))[0]
    name1 = os.path.splitext(pxm.GetProxyName("sources", s_list[1]))[0]
    # generate vn if not exists
    s1 = generate_vn(s_list[0], name0)
    s2 = generate_vn(s_list[1], name1)
    sd1 = servermanager.Fetch(s1)
    sd2 = servermanager.Fetch(s2)
    p2c = sd1.IsA("vtkPolyData") and sd2.IsA("vtkPolyData")
    # create filter
    hd = HausdorffDistance(InputA=s1, InputB=s2)
    if not p2c:
        hd.TargetDistanceMethod = 'Point-to-Point'
    SetActiveSource(hd)    # set active source to hd to find transfer function
    RenameSource("{}_{}".format(name0, name1), hd)
    
    ly = CreateLayout('Hdf_{}{}'.format(name0, name1))
    v0 = CreateRenderView(False, registrationName=name0)
    v1 = CreateRenderView(False, registrationName=name1)
    v0.ViewSize = [1024, 768]
    v1.ViewSize = [1024, 768]
    out0 = OutputPort(hd, 0)
    out1 = OutputPort(hd, 1)
    display0 = Show(out0, v0)
    display1 = Show(out1, v1)
    set_hd_output_display(display0, v0)
    set_hd_output_display(display1, v1)

    # Rescale transfer function
    distanceLUT = GetColorTransferFunction('Distance')
    distancePWF = GetOpacityTransferFunction('Distance')
    distanceLUT.ApplyPreset('hausdorff', True)
    distancePWF.ApplyPreset('hausdorff', True)
    distanceLUT.RescaleTransferFunction(0.0, 0.1)
    distancePWF.RescaleTransferFunction(0.0, 0.1)
    return (v0, v1, out0, out1)

## end=================hausdorff distance ======================


# class for screenshots
class ScreenShotHelper:
    def __init__(self):
        paraview.simple._DisableFirstRenderCameraReset()

    # fill camera variable from number list
    def fill_var(self, in_list, idx, var):
        if isinstance(var, int) or isinstance(var, float):
            var = in_list[idx]
            return 1
        ac = len(var)
        var[:] = in_list[idx: idx + len(var)]
        return ac

    def set_camera(self, v, cam):
        idx = 0
        idx += self.fill_var(cam, idx, v.CameraFocalPoint)
        idx += self.fill_var(cam, idx, v.CameraParallelProjection)
        idx += self.fill_var(cam, idx, v.CameraParallelScale)
        idx += self.fill_var(cam, idx, v.CameraPosition)
        idx += self.fill_var(cam, idx, v.CameraViewAngle)
        idx += self.fill_var(cam, idx, v.CameraViewUp)

    def take_shot(self, view, cam, filename):
        self.set_camera(view, cam)
        v_size = view.ViewSize
        view.Update()
        # create temporary file to cope utf-8 char
        if not os.path.exists("c:/tf_tmp"):
            os.makedirs("c:/tf_tmp")
        tmp_file = "c:/tf_tmp/ss.png"
        SaveScreenshot(tmp_file, view, ImageResolution=v_size, TransparentBackground=0)
        move(tmp_file, filename)


# read file or file list and render in given view
def read_and_render(file_list, v):
    HideAll(v)
    reader = read_files(file_list)
    reader_display = Show(reader, v)
    reader_display.ColorArrayName = [None, '']
    reader_display.Specular = 0.5
    show_texture(reader, v)
    v.ResetCamera()
    # add anotation
    f = file_list[0]
    path, filename = os.path.split(f)
    if len(file_list) > 1: # file list, fetch parent dir
        path, filename = os.path.split(path)
    stem = trim_last_number(os.path.splitext(filename)[0])
    path, ver = os.path.split(path)
    path, case = os.path.split(path)
    add_annotation(v, "{}\n{}\n{}".format(case, ver, stem), 28)
    add_time_annotation(v, f)
    v.Update()
    return reader


# create screenshots for given file from given cam_list    
def create_shot(file_list, cam_list, out_dir, pattern):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    cur_view = GetActiveViewOrCreate("RenderView")
    cur_view.ViewSize = [1024, 768]
    add_light_to_view(cur_view, False)
    cur_view.CenterAxesVisibility = 0
    cur_source = read_and_render(file_list, cur_view)
    ss = ScreenShotHelper()
    for i in range(0, len(cam_list)):
        ss.take_shot(cur_view, cam_list[i],
                     "{}/ss_{}_v{}.png".format(out_dir, pattern, i).replace("\\", "/"))
    Delete(cur_source)
    del cur_source
    return len(cam_list)




# read cam position from config file
def read_cam(case_file):
    if not os.path.exists(case_file):
        return None
    content = None
    with open(case_file) as f:
        content = f.readlines()
    str_list = [l.strip() for l in content if len(l) > 20]
    str_lines = [line.split(", ") for line in str_list]
    return [[float(s) for s in item] for item in str_lines if len(item) == 12]

# if data_file newer than ss_file, need update
def ss_need_update(file_list, file_cam, out_dir, pattern):
    file_pic = os.path.join("{}/ss_{}_v0.png".format(out_dir, pattern)).replace("\\", "/")
    if not os.path.exists(file_pic):
        return True
    time_config = os.path.getmtime(file_cam)
    time_data = os.path.getmtime(file_list[0])
    time_pic = os.path.getmtime(file_pic)
    if time_config > time_pic: # new cam config
        return True
    if time_data > time_pic: # new data
        return True
    return False


# execute screenshot operation(need config information)
# general operation, case/version/filanem all have their effects
def create_screenshots(dir_input, dir_output, list_case, list_ver, list_alg):
    total_num = 0
    # case/version/alg
    file_dir = []
    for ci in list_case:
        for vi in list_ver:
            file_dir.append([ci, vi, os.path.join(dir_output, ci, vi)])
    #create shot
    for item in file_dir:
        case_name = item[0]
        ver_name = item[1]
        case_files = item[2]
        cam_file = os.path.join(dir_input, case_name, "config.txt")
        if not os.path.exists(cam_file):
            print("Camera config file {} does not exist!".format(cam_file))
            continue
        cam_list = read_cam(cam_file)
        if cam_list is None or len(cam_list) < 1:
            continue
        if ver_name == "input":
            i_list = get_file(dir_input, case_name)
            pic_out_dir = os.path.join(dir_output, case_name, "input")
            if not ss_need_update(i_list, cam_file, pic_out_dir , "input"):
                print("{}/{}/{} already up-to-date".format(case_name, ver_name, "input"))
                continue
            total_num += create_shot(i_list, cam_list, pic_out_dir, "input")
        else:
            for alg in list_alg:
                file_list = get_file(case_files, alg)
                if file_list is None or len(file_list) < 1:
                    continue
                pic_out_dir = os.path.join(dir_output, case_name, ver_name)
                if not ss_need_update(file_list, cam_file, pic_out_dir, alg):
                    print("{}/{}/{} already up-to-date".format(case_name, ver_name, alg))
                    continue
                print("Updating screenshots for {}/{}/{}".format(case_name, ver_name, alg))
                total_num += create_shot(file_list, cam_list, pic_out_dir , alg)
    return total_num

# get cam config float array from view
def fill_list(res, idx, in_list):
    if isinstance(in_list, int) or isinstance(in_list, float):
        res.append(in_list)
        return 1
    ac = len(in_list)
    res[idx:idx+ac] = in_list[:]
    return ac


def build_cam_list(v):
    camera_pos = []
    idx = 0
    idx += fill_list(camera_pos, idx, v.CameraFocalPoint)
    idx += fill_list(camera_pos, idx, v.CameraParallelProjection)
    idx += fill_list(camera_pos, idx, v.CameraParallelScale)
    idx += fill_list(camera_pos, idx, v.CameraPosition)
    idx += fill_list(camera_pos, idx, v.CameraViewAngle)
    idx += fill_list(camera_pos, idx, v.CameraViewUp)
    return camera_pos


def write_dist_statistics(s, filename):
    sd = servermanager.Fetch(s)
    fd = sd.GetFieldData()
    sigma_rate = fd.GetArray("sigma_rate")
    if sigma_rate is None or sigma_rate.GetDataSize() != 6:
        print("Warning! no statistics info in hausdorff output")
        return
    sigma_num = fd.GetArray("sigma_num")
    mean_total = fd.GetArray("mean_total").GetTuple1(0)
    mean_positive = fd.GetArray("mean_positive").GetTuple1(0)
    mean_negative = fd.GetArray("mean_negative").GetTuple1(0)
    max_positive = fd.GetArray("max_positive").GetTuple1(0)
    max_negative = fd.GetArray("max_negative").GetTuple1(0)
    standard_deviation = fd.GetArray("standard_deviation").GetTuple1(0)

    # sigma_rate = [0.01, 0.02, 0.23, 0.38, 0.21, 0.1]
    # sigma_num = [10, 20, 230, 380, 210, 100]
    # mean_total = 0.01
    # mean_positive = 0.02
    # mean_negative = -0.01
    # max_positive = 0.1
    # max_negative = -0.1
    # standard_deviation = 0.11
    f_sts = open(filename, "w", encoding='utf-8')
    f_sts.write("{} {} {} {} {} {}\n".format(sigma_rate.GetTuple1(0), sigma_rate.GetTuple1(1), sigma_rate.GetTuple1(2),
                                              sigma_rate.GetTuple1(3), sigma_rate.GetTuple1(4), sigma_rate.GetTuple1(5)))
    f_sts.write("{} {} {} {} {} {}\n".format(sigma_num.GetTuple1(0), sigma_num.GetTuple1(1), sigma_num.GetTuple1(2),
                                              sigma_num.GetTuple1(3), sigma_num.GetTuple1(4), sigma_num.GetTuple1(5)))
    f_sts.write("{}\n".format(mean_total))
    f_sts.write("{}\n".format(mean_positive))
    f_sts.write("{}\n".format(mean_negative))
    f_sts.write("{}\n".format(max_positive))
    f_sts.write("{}\n".format(max_negative))
    f_sts.write("{}\n".format(standard_deviation))
    f_sts.close()

# screen shot for customized application
# only case list is needed
def create_hausdorff_shot(dir_input, dir_output, list_case):
    print("Creating hausdorf distance screenshots")
    print("Case: {}".format(list_case))
    total_num = 0
    for case in list_case:
        i_list = get_file(dir_input, case)
        out_dir = os.path.join(dir_output, case, "hausdorff_A2B")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_dir2 = os.path.join(dir_output, case, "hausdorff_B2A")
        if not os.path.exists(out_dir2):
            os.makedirs(out_dir2)
        #if not ss_need_update(i_list, cam_file, pic_out_dir , "input"):
        #        print("{}/{}/{} already up-to-date".format(case_name, ver_name, "input"))
        #        continue
        (v0, v1, out0, out1) = show_hausdorff_dist(i_list)
        write_dist_statistics(out0, "{}/dist.sts".format(out_dir))
        write_dist_statistics(out1, "{}/dist.sts".format(out_dir2))
        if v0 is None:
            continue
        ss = ScreenShotHelper()
        # standard
        std_cam = []
        co = CameraObject(out0)
        co.set_camera(v0, "x+")
        std_cam.append(build_cam_list(v0))
        co.set_camera(v0, "x-")
        std_cam.append(build_cam_list(v0))
        co.set_camera(v0, "y+")
        std_cam.append(build_cam_list(v0))
        co.set_camera(v0, "y-")
        std_cam.append(build_cam_list(v0))
        co.set_camera(v0, "z+")
        std_cam.append(build_cam_list(v0))
        co.set_camera(v0, "z-")
        std_cam.append(build_cam_list(v0))
        for i in range(0, 6):
            ss.take_shot(v0, std_cam[i],
                         "{}/ss___hd_v{}.png".format(out_dir, i).replace("\\", "/"))
            ss.take_shot(v1, std_cam[i],
                         "{}/ss___hd_v{}.png".format(out_dir2, i).replace("\\", "/"))
        total_num = total_num + 12
        cam_file = os.path.join(dir_input, case, "config.txt")
        if not os.path.exists(cam_file):
            print("Camera config file {} does not exist!".format(cam_file))
            continue
        cam_list = read_cam(cam_file)
        for i in range(0, len(cam_list)):
            ss.take_shot(v0, cam_list[i],
                         "{}/ss___hd_v{}.png".format(out_dir, i + 6).replace("\\", "/"))
            ss.take_shot(v1, cam_list[i],
                         "{}/ss___hd_v{}.png".format(out_dir2, i + 6).replace("\\", "/"))
        total_num = total_num + len(cam_list) * 2
    return total_num


# brief external interface interpreted by PVpython
def create_screenshots_wrap(dir_input, dir_output, file_config):
    # data to be compared
    # get all concerned file names
    list_case, list_ver, list_alg = read_compare_config(file_config)
    print("Start screenshot: ")
    print("case: {}".format(list_case))
    print("ver: {}".format(list_ver))
    print("filename: {}".format(list_alg))
    total_n = 0
    if len(list_ver) < 1 or list_ver[0] == "__hausdorff":
        total_n = create_hausdorff_shot(dir_input, dir_output, list_case)
    else:
        total_n = create_screenshots(dir_input, dir_output, list_case, list_ver, list_alg)
    f_config = open(file_config, "w", encoding='utf-8')
    f_config.write("{}\n".format(total_n))
    f_config.close()


if __name__ == "__main__":
    dir_input = sys.argv[1]
    dir_output = sys.argv[2]
    file_config = sys.argv[3]
    create_screenshots_wrap(dir_input, dir_output, file_config)
