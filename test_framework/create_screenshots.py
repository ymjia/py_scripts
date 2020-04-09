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
from paraview import vtk
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

def show_hausdorff_dist(s_name_list, critical_dist, max_dist):
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
    distanceLUT.ApplyPreset('hausdorff_dir', True)
    distancePWF.ApplyPreset('hausdorff_dir', True)
    distanceLUT.RescaleTransferFunction(-0.05, 0.05)
    distancePWF.RescaleTransferFunction(-0.05, 0.05)
    return (v0, v1, out0, out1)

def write_dist_statistics(s, filename, in_file):
    sd = servermanager.Fetch(s)
    fd = sd.GetFieldData()
    sigma_rate = fd.GetArray("six_sigma_rate")
    if sigma_rate is None or sigma_rate.GetDataSize() != 6:
        print("Warning! no statistics info in hausdorff output")
        return
    sigma_num = fd.GetArray("six_sigma_num")
    mean_total = fd.GetArray("mean_total").GetTuple1(0)
    mean_positive = fd.GetArray("mean_positive").GetTuple1(0)
    mean_negative = fd.GetArray("mean_negative").GetTuple1(0)
    max_positive = fd.GetArray("max_positive").GetTuple1(0)
    max_negative = fd.GetArray("max_negative").GetTuple1(0)
    standard_deviation = fd.GetArray("standard_deviation").GetTuple1(0)

    # sigma_rate = vtk.vtkDoubleArray()
    # sigma_rate.SetNumberOfComponents(1)
    # sigma_rate.SetNumberOfTuples(6)
    # sigma_num = vtk.vtkDoubleArray()
    # sigma_num.SetNumberOfComponents(1)
    # sigma_num.SetNumberOfTuples(6)
    # l_sigma_rate = [0.01, 0.02, 0.23, 0.38, 0.21, 0.1]
    # l_sigma_num = [10, 20, 230, 380, 210, 100]
    # for i in range(0, 6):
    #     sigma_rate.SetTuple1(i, l_sigma_rate[i])
    #     sigma_num.SetTuple1(i, l_sigma_num[i])
    # mean_total = 0.01
    # mean_positive = 0.02
    # mean_negative = -0.01
    # max_positive = 0.1
    # max_negative = -0.1
    # standard_deviation = 0.11
    f_sts = open(filename, "w", encoding='utf-8')
    f_sts.write("{}\n".format(" ".join(map(str, [sigma_rate.GetTuple1(i) for i in range(0, 6)]))))
    f_sts.write("{}\n".format(" ".join(map(str, [sigma_num.GetTuple1(i) for i in range(0, 6)]))))
    f_sts.write("{}\n".format(mean_total))
    f_sts.write("{}\n".format(mean_positive))
    f_sts.write("{}\n".format(mean_negative))
    f_sts.write("{}\n".format(max_positive))
    f_sts.write("{}\n".format(max_negative))
    f_sts.write("{}\n".format(standard_deviation))
    f_sts.write("{}\n".format(in_file))
    f_sts.close()
## end=================hausdorff distance ======================


# class for screenshots with config
class ScreenShotHelper:
    def __init__(self, sc):
        paraview.simple._DisableFirstRenderCameraReset()
        self._sc = sc

    def take_shot(self, view, cam, filename):
        trans_bg = self._sc.config_val("transparent_background", "False") == "True"
        co = CameraObject()
        if not co.read_camera_from_str(cam):
            print("Warning! cannot decode camera from string {}".format(cam))
            return
        co.set_camera(view)
        v_size = view.ViewSize
        view.Update()
        # create temporary file to cope utf-8 char
        if not os.path.exists("c:/tf_tmp"):
            os.makedirs("c:/tf_tmp")
        tmp_file = "c:/tf_tmp/ss.png"
        SaveScreenshot(tmp_file, view,
                       ImageResolution=v_size, TransparentBackground=trans_bg)
        move(tmp_file, filename)

    # read file or file list and render in given view
    def read_and_render(self, file_list, v):
        specular = self._sc.config_val("rep_specular", "True")
        HideAll(v)
        reader = read_files(file_list)
        reader_display = Show(reader, v)
        reader_display.ColorArrayName = [None, '']
        if specular == "True":
            reader_display.Specular = 0.5
        else:
            reader_display.Specular = 0.0
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
    def create_shot(self, file_list, cam_list, out_dir, pattern):
        v_w = int(self._sc.config_val("view_width", 1024))
        v_h = int(self._sc.config_val("view_height", 768))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        cur_view = GetActiveViewOrCreate("RenderView")
        cur_view.ViewSize = [v_w, v_h]
        cur_view.CenterAxesVisibility = 0
        cur_source = self.read_and_render(file_list, cur_view)
        for i in range(0, len(cam_list)):
            self.take_shot(cur_view, cam_list[i],
                         "{}/ss_{}_v{}.png".format(out_dir, pattern, i).replace("\\", "/"))
        Delete(cur_source)
        del cur_source
        return len(cam_list)

    # if data_file newer than ss_file, need update
    def ss_need_update(self, file_list, file_cam, out_dir, pattern):
        if self._sc.config_val("ss_force_update", "False") == "True":
            return True
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

# read cam position from config file
def read_cam(case_file):
    if not os.path.exists(case_file):
        return None
    content = None
    with open(case_file) as f:
        content = f.readlines()
    return [l.strip() for l in content if len(l) > 20]




# execute screenshot operation(need config information)
# general operation, case/version/filanem all have their effects
def create_screenshots(sc):
    total_num = 0
    dir_input = sc.config_map["dir_i"]
    dir_output = sc.config_map["dir_o"]
    # case/version/alg
    ss = ScreenShotHelper(sc)
    file_dir = []
    for ci in sc.list_case:
        for vi in sc.list_ver:
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
            if not ss.ss_need_update(i_list, cam_file, pic_out_dir , "input"):
                print("{}/{}/{} already up-to-date".format(case_name, ver_name, "input"))
                continue
            total_num += ss.create_shot(i_list, cam_list, pic_out_dir, "input")
        else:
            for alg in sc.list_alg:
                file_list = get_file(case_files, alg)
                if file_list is None or len(file_list) < 1:
                    continue
                pic_out_dir = os.path.join(dir_output, case_name, ver_name)
                if not ss.ss_need_update(file_list, cam_file, pic_out_dir, alg):
                    print("{}/{}/{} already up-to-date".format(case_name, ver_name, alg))
                    continue
                print("Updating screenshots for {}/{}/{}".format(case_name, ver_name, alg))
                total_num += ss.create_shot(file_list, cam_list, pic_out_dir , alg)
    return total_num



# screen shot for customized application
# only case list is needed
def create_hausdorff_shot(sc):
    print("Creating hausdorf distance screenshots")
    print("Case: {}".format(sc.list_case))
    #get parameter
    hd_critical_dist = float(sc.config_val("hd_critical_dist", "0.02"))
    hd_max_dist = float(sc.config_val("hd_max_dist", "0.1"))

    dir_input = sc.config_map["dir_i"]
    dir_output = sc.config_map["dir_o"]
    total_num = 0
    for case in sc.list_case:
        i_list = get_file(dir_input, case)
        out_dir = os.path.join(dir_output, case, "hausdorff_A2B")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_dir2 = os.path.join(dir_output, case, "hausdorff_B2A")
        if not os.path.exists(out_dir2):
            os.makedirs(out_dir2)
        (v0, v1, out0, out1) = show_hausdorff_dist(i_list)
        write_dist_statistics(out0, "{}/dist.sts".format(out_dir), i_list[0])
        write_dist_statistics(out1, "{}/dist.sts".format(out_dir2), i_list[1])
        if v0 is None:
            continue
        ss = ScreenShotHelper()
        # standard
        std_cam = []
        co = CameraObject()
        co.create_default_cam_angle(out0, "x+")
        std_cam.append(co.generate_camera_str())
        co.create_default_cam_angle(out0, "x-")
        std_cam.append(co.generate_camera_str())
        co.create_default_cam_angle(out0, "y+")
        std_cam.append(co.generate_camera_str())
        co.create_default_cam_angle(out0, "y-")
        std_cam.append(co.generate_camera_str())
        co.create_default_cam_angle(out0, "z+")
        std_cam.append(co.generate_camera_str())
        co.create_default_cam_angle(out0, "z-")
        std_cam.append(co.generate_camera_str())
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
def create_screenshots_wrap(file_config):
    # data to be compared
    # get all concerned file names
    sc = SessionConfig()
    if not sc.read_config(file_config):
        print("Warning! Fail to read config file {}".format(file_config))
        return
    if sc.list_case is None:
        print("Error! no config file in {}".format(file_config))
        return
    print("Start screenshot: ==============")
    sc.print_config()
    print("===============================")
    total_n = 0
    if len(sc.list_ver) < 1 or sc.list_ver[0] == "__hausdorff":
        total_n = create_hausdorff_shot(sc)
    else:
        total_n = create_screenshots(sc)
    f_config = open(file_config, "w", encoding='utf-8')
    f_config.write("{}\n".format(total_n))
    f_config.close()


if __name__ == "__main__":
    file_config = sys.argv[1]
    create_screenshots_wrap(file_config)
