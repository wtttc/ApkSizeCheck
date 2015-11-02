#! /usr/bin/env python
# -*- coding: utf-8 -*-
import getopt
import os
import sys
import re
import shutil
import utils

__author__ = 'tiantong'


def estimate_target_file(apk_file, target, out_floder=None):
    # 确保输出的临时文件夹存在
    if out_floder is None:
        out_floder = utils.cur_file_dir()

    # 复制临时文件文件夹
    temp_zip_floder = os.path.join(out_floder, "temp_zip")
    # 临时zip文件
    temp_zip_file = os.path.join(out_floder, "temp_zip.zip")
    # 临时解压文件夹
    out_floder = os.path.join(out_floder, "temp")

    if not os.path.isdir(out_floder):
        os.makedirs(out_floder)
    if not os.path.isdir(temp_zip_floder):
        os.makedirs(temp_zip_floder)

    # 获取需要检查的set文件
    search_target_set = utils.read_set_from_file(target)
    if search_target_set is None:
        exit()

    for item in search_target_set:
        print("search regular: " + item)
    print("")

    # 获取没有拓展名的文件名
    apk_dir = os.path.split(apk_file)[-1].split(".")[0]

    apk_size = utils.get_path_size(apk_file)
    print("apk_file:%s size: %s" % (apk_dir, utils.get_size_in_nice_string(apk_size)))
    print("")

    # 解压文件夹以便分析
    print("start to unzip apk")
    utils.surely_rmdir(out_floder)
    utils.unzip_dir(apk_file, out_floder)

    for p, d, f in os.walk(out_floder):
        for file in f:
            for item in search_target_set:
                sp = re.findall(item, file)
                count = len(sp)
                if count == 0:
                    continue
                file_path = os.path.join(p, file)
                suffix_index = file_path.find(out_floder)
                suffix = file_path[suffix_index + len(out_floder) + 1:]
                out_file_path = os.path.join(temp_zip_floder, suffix)
                out_file_floder = os.path.dirname(out_file_path)
                # print("find match:" + file)
                # print("temp_zip_floder:" + temp_zip_floder)
                # print("suffix:" + suffix)
                # print("out_file_path:" + out_file_path)
                # print("target path:" + os.path.dirname(out_file_path))

                # 保证指定drawable文件夹存在
                if not os.path.exists(out_file_floder):
                    os.makedirs(out_file_floder)
                if os.path.exists(file_path) and not os.path.exists(out_file_path):
                    shutil.copy(file_path, out_file_path)

    file_count = 0
    for _, _, f in os.walk(temp_zip_floder):
        fileLength = len(f)
        if fileLength != 0:
            file_count += fileLength
    utils.zip_dir(temp_zip_floder, temp_zip_file)

    print("")
    print("Found %s files match set" % file_count)
    print("Expanded size: " + utils.get_size_in_nice_string(utils.get_path_size(temp_zip_floder)))
    print("Occupied apk size(estimated): " + utils.get_size_in_nice_string(utils.get_path_size(temp_zip_file)))

    # 清除临时输出文件
    utils.surely_rmdir(out_floder)
    utils.surely_rmdir(temp_zip_floder)
    utils.surely_rmfile(temp_zip_file)


def usage():
    print '------------apkimagecheck.py usage:------------'
    print '-h, --help     : print help message.'
    print '-a, --apk      : apk file'
    print '-t, --target   : target files'
    print '-o, --out      : temporary output folder'
    print '----------------------------------------'


def exit():
    usage()
    print("")
    sys.exit(1)


if "__main__" == __name__:
    apk_file = None
    target = None
    out_floder = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ha:t:o:", ["help", "output="])

        # check all param
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage();
                sys.exit(1);
            if opt in ("-a", "--apk"):
                apk_file = arg
            if opt in ("-t", "--target"):
                target = arg
            if opt in ("-o", "--out"):
                out_floder = arg

    except getopt.GetoptError, e:
        print("getopt error! " + e.msg);
        exit()

    if apk_file is None or target is None or not os.path.isfile(apk_file) or not os.path.isfile(target):
        exit()

    print("")
    estimate_target_file(apk_file, target, out_floder)
    print("")
