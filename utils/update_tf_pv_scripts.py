# -*- coding: utf-8 -*-
## @file update_tf_pv_scripts

import os.path
from os.path import join
from shutil import copy2

# dir_base: base dir for python scripts
# div_pv_base: pv plugin scripts dir
# dir_dst:  paraview install dir
def update_scripts(dir_base, dir_pv_base, dir_dst):
    # update bin scripts
    bin_list = ["deviation_doc.py", "screenshot_doc.py"]
    dst_bin = os.path.join(dir_dst, "bin")
    for f in bin_list:
        print("copy from {} to {}".format(join(dir_pv_base, f), join(dst_bin, f)))
        copy2(join(dir_pv_base, f), join(dst_bin, f))

    # update test_framework
    dst_dir = join(dir_dst, "bin", "Lib", "site-packages", "test_framework")
    src_dir = join(dir_base, "test_framework")
    tgt_list = ["utils.py", "create_screenshots.py", "generate_docx.py", "framework_util.py"]
    for f in tgt_list:
        print("copy from {} to {}".format(join(src_dir, f), join(dst_dir, f)))
        copy2(join(src_dir, f), join(dst_dir, f))

dir_base = "d:/dev/py_scripts"
dir_pv_base = "d:/dev/paraview_plugin/scripts"
dir_dst = "d:/ParaView57_r"
update_scripts(dir_base, dir_pv_base, dir_dst)
