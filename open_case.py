# -*- coding: utf-8 -*-
## @file framework_util.py
## @brief utilize functions for test framework
## @author jiayanming

import os
import sys

dir_py_module = os.path.join(os.getcwd(), "..", "Sn3D_plugins", "scripts", "pv_module")
sys.path.append(dir_py_module)
from framework_util import *

dir_in = "d:/data/test_framwork/output"

load_state_files(dir_in, "case1", "smooth", ["v11", "v12"])
load_state_files(dir_in, "case2", "merge", ["v11", "v12"])

