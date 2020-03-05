# -*- coding: utf-8 -*-
## @file get_paraview.py
## @brief get_paraview
## @author jiayanming

from pyunpack import Archive
import subprocess
import os.path
import sys
import shutil

def get_file_from_ftp(filename):
    try:
        with ftplib.FTP("10.10.1.80", "yf", "123456") as ftp:
            ftp.cwd('/Test')
            with open(filename, 'wb') as f:
                ftp.retrbinary("RETR ParaView.rar", f.write)
                f.close()
    except ftplib.all_errors:
        print("FTP error!")
    return 0


def git_clone(repo, path_to):
    proc = subprocess.run(["git", "clone", repo, path_to], shell=True)
    if proc.returncode != 0:
        print("Error! git clone failed")
        return 1
    return 0


def unpack_file(filename, path_to):
    Archive(filename).extractall(path_to)


def get_paraview(pv_git, root_dir):
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    # get from ftp
    pv_rar = os.path.join(tmp_dir, "ParaView.rar")
    get_file_from_ftp(pv_rar)
    pv_dir = os.path.join(root_dir, "ParaView")
    if os.path.exists(pv_dir):
        shutil.rmtree(pv_dir)
    unpack_file(pv_rar, pv_dir)

    # clone from git
    tmp_dir = os.path.join(root_dir, "tmp")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    git_clone(pv_git, tmp_dir)

    # copy skip exists
    shutil.move(os.path.join(tmp_dir, ".git"), os.path.join(pv_dir, ".git"))
    shutil.rmtree(tmp_dir)

    proc = subprocess.run(["git", "checkout", "."], shell=True)

    return 0


get_paraview()
