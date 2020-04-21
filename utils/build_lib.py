# -*- coding: utf-8 -*-
## @file build_lib.py
## @brief run cmake and vs build

import os
import subprocess

cmake_tool = "C:/Program Files/CMake/bin/cmake.exe"

def build_lib(cur_path):
    proc = subprocess.run([cmake_tool, "--build", ".", "--config", "Release", "--target", "INSTALL"], shell=True, cwd = cur_path)
    return proc.returncode


cwd = os.getcwd()
build_lib(cwd)
