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
from paraview.simple import GetDisplayProperties

from test_framework.utils import SessionConfig
from test_framework.utils import g_config
from test_framework.framework_util import *
from test_framework.generate_docx import HausdorffSts

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

def set_legend_prop(lgd, nominal_dist, critical_dist, max_dist):
    
    if g_config.config_val("hd_legend_type", "Vertical") == "Vertical":
        lgd.Orientation = "Vertical"
        lgd.WindowLocation = "LowerRightCorner"
        lgd.TextPosition = 'Ticks left/bottom, annotations right/top'
    else:
        lgd.Orientation = "Horizontal"
        lgd.WindowLocation = "LowerCenter"
    lgd.LabelFontSize = 12
    lgd.ScalarBarLength = 0.66
    lgd.TitleColor = [0, 0, 0]
    lgd.LabelColor = [0, 0, 0]
    lgd.UseCustomLabels = 1
    lgd.AddRangeLabels = 0
    lgd.CustomLabels = [-max_dist, -critical_dist, -nominal_dist, nominal_dist, critical_dist, max_dist]
    

def show_hausdorff_dist_from_name_list(s_name_list):
    #get parameter
    s_num = len(s_name_list)
    if s_num != 2:
        print("Error! 2 source need to be selected, current source:")
        print(s_name_list)
        return (None, None, None)
    s_list = []
    for name in s_name_list:
        reader = read_files([name])
        if reader is not None:
            s_list.append(reader)
    if len(s_list) != 2:
        print("2 poly mesh needed, now got {}".format(len(s_list)))
        return (None, None, None)

    if not load_local_plugin("Utils", "HausdorffDistance", globals()):
        print("Error! Fail to load Utils Plugin!")
        return (None, None, None)
    print("###{}".format("HausdorffDistance" in globals()))
    return show_hausdorff_dist_from_slist(s_list)


def show_hausdorff_dist_from_slist(s_list):
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
    max_dist = float(g_config.config_val("hd_max_dist", "0.3"))
    hd = HausdorffDistance(InputA=s1, InputB=s2)
    hd.MaxSearchRadius = max_dist
    if not p2c:
        hd.TargetDistanceMethod = 'Point-to-Point'
    RenameSource("{}_{}".format(name0, name1), hd)
    return show_hausdorff_dist_from_hd(hd, name0, name1)


def show_hausdorff_dist_from_hd(hd, name0="A", name1="B"):
    nominal_dist = float(g_config.config_val("hd_nominal_dist", "0.03"))
    critical_dist = float(g_config.config_val("hd_critical_dist", "0.05"))
    max_dist = float(g_config.config_val("hd_max_dist", "0.3"))#hd.MaxSearchRadius

    SetActiveSource(hd)    # set active source to hd to find transfer function
    
    ly = CreateLayout('Hdf_{}{}'.format(name0, name1))
    v0 = CreateRenderView(False, registrationName=name0)
    v1 = CreateRenderView(False, registrationName=name1)
    pos = ly.SplitHorizontal(0, 0.5)
    ly.AssignView(pos, v0)
    ly.AssignView(pos+1, v1)

    out0 = OutputPort(hd, 0)
    out1 = OutputPort(hd, 1)
    display0 = Show(out0, v0)
    display1 = Show(out1, v1)
    set_hd_output_display(display0, v0)
    set_hd_output_display(display1, v1)

    # Rescale transfer function
    distanceLUT = GetColorTransferFunction('Distance')
    distancePWF = GetOpacityTransferFunction('Distance')
    distanceLUT.ColorSpace = 'RGB'
    eps = 1e-8
    max_eps = max_dist * 1.05
    distanceLUT.RGBPoints = [-max_dist, 0, 0, 1, -critical_dist, 0, 1, 1,
                             -nominal_dist - eps, 0, 1, 1, -nominal_dist, 0, 1, 0,
                             nominal_dist, 0, 1, 0, nominal_dist + eps, 1, 1, 0,
                             critical_dist, 1, 1, 0, max_dist, 1, 0, 0]
    distancePWF.Points = [-max_dist, 1.0, 0.5, 0, max_dist, 1.0, 0.5, 0]
    
    # legend position
    lgd_v0 = GetScalarBar(distanceLUT, v0)
    lgd_v1 = GetScalarBar(distanceLUT, v1)
    set_legend_prop(lgd_v0, nominal_dist, critical_dist, max_dist)
    set_legend_prop(lgd_v1, nominal_dist, critical_dist, max_dist)
    return (v0, v1, hd)


def write_dist_statistics(sd, filename, in_file):
    sts = HausdorffSts()
    sts.get_from_hd(sd)
    sts.in_file = in_file
    sts.write_to_file(filename)
## end=================hausdorff distance ======================

## ==================Camera position Setting =================
def start_camera_set_session(names, f_config):
    view_height = int(g_config.config_val("ss_view_height", "768"))
    view_width = int(g_config.config_val("ss_view_width", "1024"))

    cn = len(read_cam(f_config))
    s = read_files(names)
    if s is None:
        print("Error! Fail to open file {}".format(names))
        return
    v = CreateView("RenderView")
    v.ViewSize = [view_width, view_height]
    v.OrientationAxesVisibility = 1
    # set default camera

    it = v.GetInteractor()
    ant = add_annotation(v, "'C': Record Current Camera\n'Q': Finish and quit\n'R': Reset Camera\n'Ctrl+Alt+D': Delete All Record\nTotal: {}".format(cn), 16)
    #it.AddObserver("KeyReleaseEvent", #KeyPressEvent",
    it.AddObserver("KeyPressEvent",
                   lambda o, e, source=s, conf = f_config, txt = ant: CameraKey(o, e, source, conf, txt))
    dp = Show(s, v)
    set_default_view_display(v)
    set_default_display(dp)
    # set initial view point
    co = CameraObject()
    co.create_default_cam_angle(s, "x+")
    co.set_camera(v)
    v.CenterOfRotation = v.CameraFocalPoint
    v.Update()
    Interact(v)
    Delete(v)
    del v


def CameraKey(obj, event, s, conf, txt):
    k = obj.GetKeySym()
    if k == "q":
        return
    elif k == "c":
        v = GetActiveView()
        co = CameraObject()
        co.get_camera(v)
        cam_str = co.generate_camera_str()
        f = open(conf, "a")
        f.writelines("\n" + cam_str)
        f.close()
        cn = len(read_cam(conf))
        txt.Text = "'C': Record Current Camera\n'Q': Finish and quit\n'R': Reset Camera\n'Ctrl+Alt+D': Delete All Record\nTotal: {}".format(cn)
        v.Update()
        Render()
    elif k == "r":
        v = GetActiveView()
        co = CameraObject()
        co.create_default_cam_angle(s, "x+")
        co.set_camera(v)
        v.Update()
        Render()
    elif k == 'd':
        if obj.GetControlKey() == 0 or obj.GetAltKey() == 0:
            return
        #clear existing angle
        f = open(conf, "w")
        f.close()
        cn = len(read_cam(conf))
        txt.Text = "'C': Record Current Camera\n'Q': Finish and quit\n'R': Reset Camera\n'Ctrl+Alt+D': Delete All Record\nTotal: {}".format(cn)
        v = GetActiveView()
        v.Update()
        Render()
    else:
        return


## end===============Camera position Setting =================


# class for screenshots with config
class ScreenShotHelper:
    def __init__(self):
        paraview.simple._DisableFirstRenderCameraReset()
        self._v = None

    def __del__(self):
        if self._v is not None:
            Delete(self._v)

    # static methed, view need not be associated to self._v
    def take_shot(self, view, cam, filename):
        view_height = int(g_config.config_val("ss_view_height", "768"))
        view_width = int(g_config.config_val("ss_view_width", "1024"))

        trans_bg = g_config.config_val("ss_transparent_bg", "False") == "True"
        co = CameraObject()
        if not co.read_camera_from_str(cam):
            print("Warning! cannot decode camera from string {}".format(cam))
            return
        co.set_camera(view)
        v_size = [view_width, view_height]
        view.Update()
        # create temporary file to cope utf-8 char
        if not os.path.exists("c:/tf_tmp"):
            os.makedirs("c:/tf_tmp")
        tmp_file = "c:/tf_tmp/ss.png"
        SaveScreenshot(tmp_file, view,
                       ImageResolution=v_size, TransparentBackground=trans_bg)
        #in case view bug happenned in savescreenshot
        if view.CameraPosition.GetData() != co.CameraPosition:
            co.set_camera(view)
            view.Update()
            SaveScreenshot(tmp_file, view,
                           ImageResolution=v_size, TransparentBackground=trans_bg)
        move(tmp_file, filename)

    # read file or file list and render in given view
    def read_and_render(self, file_list, v, case=None, ver=None):
        specular = g_config.config_val("ss_specular", True)
        HideAll(v)
        reader = read_files(file_list)
        if reader is None:
            print("Warning! ss_helper:read_and_render {} cannot read".format(file_list))
            return None
        reader_display = Show(reader, v)
        set_default_view_display(v)
        set_default_display(reader_display)
        if specular:
            reader_display.Specular = 0.5
        else:
            reader_display.Specular = 0.0
        #if g_config.config_val("ss_enable_color", False):
        if g_config.config_val("ss_enable_texture", True):
            show_texture(reader, v)
        v.ResetCamera()
        # add anotation
        f = file_list[0]
        path, filename = os.path.split(f)
        if len(file_list) > 1: # file list, fetch parent dir
            path, filename = os.path.split(path)
        stem = trim_last_number(os.path.splitext(filename)[0])
        if ver is None and case is None:
            path, ver = os.path.split(path)
            path, case = os.path.split(path)

        add_annotation(v, "{}\n{}\n{}".format(case, ver, stem), 28)
        add_time_annotation(v, f)
        v.Update()
        return reader

    # create screenshots for given file from given cam_list    
    def create_shot(self, file_list, cam_list, out_dir, pattern, case=None, ver=None):
        v_w = int(g_config.config_val("ss_view_width", 1024))
        v_h = int(g_config.config_val("ss_view_height", 768))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        if self._v is None:
            self._v = CreateView("RenderView")
        #cur_view = CreateView("RenderView")
        cur_view = self._v
        cur_view.CenterAxesVisibility = 0
        cur_source = self.read_and_render(file_list, cur_view, case, ver)
        if cur_source is None:
            return 0
        for i in range(0, len(cam_list)):
            self.take_shot(cur_view, cam_list[i],
                         "{}/ss_{}_v{}.png".format(out_dir, pattern, i).replace("\\", "/"))
        Delete(cur_source)
        del cur_source
        return len(cam_list)

    # if data_file newer than ss_file, need update
    def ss_need_update(self, file_list, file_cam, out_dir, pattern):
        if g_config.config_val("ss_force_update", False) == True:
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
        return []
    content = None
    with open(case_file) as f:
        content = f.readlines()
    if content is None:
        return []
    return [l.strip() for l in content if len(l) > 20]




# execute screenshot operation(need config information)
# general operation, case/version/filanem all have their effects
def create_screenshots(sc, cb=None):
    print("Creating screen shot:")
    sc.print_config()
    total_num = 0
    dir_input = sc.dir_i
    dir_output = sc.dir_o
    # case/version/alg
    ss = ScreenShotHelper()
    file_dir = []
    for ci in sc.list_case:
        for vi in sc.list_ver:
            file_dir.append([ci, vi, os.path.join(dir_output, ci, vi)])
    #create shot
    if cb is not None:
        cb(5)
    ss_num = float(len(file_dir))
    for ss_idx, item in enumerate(file_dir):
        if cb is not None:
            cb(ss_idx / ss_num * 90 + 5)
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
            total_num += ss.create_shot(i_list, cam_list, pic_out_dir, "input",
                                        case_name, ver_name)
        else:
            for alg in sc.list_alg:
                file_list = get_file(case_files, alg)
                if file_list is None or len(file_list) < 1:
                    print("Warning! No file in {}".format(case_files))
                    continue
                pic_out_dir = os.path.join(dir_output, case_name, ver_name)
                if not ss.ss_need_update(file_list, cam_file, pic_out_dir, alg):
                    print("{}/{}/{} already up-to-date".format(case_name, ver_name, alg))
                    continue
                print("Updating screenshots for {}/{}/{}".format(case_name, ver_name, alg))
                total_num += ss.create_shot(file_list, cam_list, pic_out_dir , alg,
                                            case_name, ver_name)
    if cb is not None:
        cb(100)
    return total_num



# screen shot for customized application
# only case list is needed
# 
def create_hausdorff_shot(sc):
    print("Creating hausdorf distance screenshots")
    print("Case: {}".format(sc.list_case))
    
    dir_input = sc.dir_i
    dir_output = sc.dir_o

    nominal_dist = float(g_config.config_val("hd_nominal_dist", "0.03"))
    critical_dist = float(g_config.config_val("hd_critical_dist", "0.05"))
    max_dist = float(g_config.config_val("hd_max_dist", "0.3"))

    total_num = 0
    for case in sc.list_case:
        tmp_dir = os.path.join(dir_output, case)
        i_list = get_file(dir_input, case)
        out_dir = os.path.join(tmp_dir, "hausdorff_A2B")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        out_dir2 = os.path.join(tmp_dir, "hausdorff_B2A")
        if not os.path.exists(out_dir2):
            os.makedirs(out_dir2)
        (v0, v1, hd) = show_hausdorff_dist(i_list)
        if v0 is None:
            continue
        set_default_view_display(v0)
        set_default_view_display(v1)
        sd0 = servermanager.Fetch(hd, idx=0)
        sd1 = servermanager.Fetch(hd, idx=1)
        f_0 = i_list[0]
        f_1 = i_list[1]
        # findout filename str
        write_dist_statistics(sd0, "{}/dist.sts".format(out_dir), f_0)
        write_dist_statistics(sd1, "{}/dist.sts".format(out_dir2), f_1)
        cam_file = os.path.join(dir_input, case, "config.txt")
        cam_list = read_cam(cam_file)
        total_num += create_shot_for_hd(hd, v0, v1, tmp_dir, cam_list)
        Delete(v0)
        Delete(v1)
        del v0
        del v1
    return total_num

        
def create_shot_for_hd(hd, v0, v1, tmp_dir, cam_list):
    out_dir = os.path.join(tmp_dir, "hausdorff_A2B")
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_dir2 = os.path.join(tmp_dir, "hausdorff_B2A")
    if not os.path.exists(out_dir2):
        os.makedirs(out_dir2)

    camera_type = g_config.config_val("ss_default_camera_type", "4_quadrant")
    total_num = 0
    out0 = OutputPort(hd, 0)
    out1 = OutputPort(hd, 1)
    ss = ScreenShotHelper()
    # standard
    std_cam = []
    co = CameraObject()
    if camera_type == "6_axis":
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
    else:
        co.create_4_cam_angle(out0, "x+y+")
        std_cam.append(co.generate_camera_str())
        co.create_4_cam_angle(out0, "x+y-")
        std_cam.append(co.generate_camera_str())
        co.create_4_cam_angle(out0, "x-y+")
        std_cam.append(co.generate_camera_str())
        co.create_4_cam_angle(out0, "x-y-")
        std_cam.append(co.generate_camera_str())

    std_cam_num = len(std_cam)
    for i in range(0, std_cam_num):
        ss.take_shot(v0, std_cam[i],
                     "{}/ss___hd_v{}.png".format(out_dir, i).replace("\\", "/"))
        ss.take_shot(v1, std_cam[i],
                     "{}/ss___hd_v{}.png".format(out_dir2, i).replace("\\", "/"))
    total_num = total_num + std_cam_num * 2
    if len(cam_list) > 0:
        for i in range(0, len(cam_list)):
            ss.take_shot(v0, cam_list[i],
                         "{}/ss___hd_v{}.png".format(out_dir, i + std_cam_num).replace("\\", "/"))
            ss.take_shot(v1, cam_list[i],
                         "{}/ss___hd_v{}.png".format(out_dir2, i + std_cam_num).replace("\\", "/"))
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
