#! /usr/bin/env python
# -*- coding: utf-8 -*-
import getopt
import os
import sys

from PIL import Image
import numpy

import utils

__author__ = 'tiantong'

ALPHA_IMAGE_FORMAT = [".png"]
LIMIT_IMAGE_FORMAT = [".png", ".jpg", ".jpeg", ".gif", ".bmp"]


def check_img_mode(filepath, value=255):
    try:
        img = Image.open(filepath)
    except Exception, ex:
        err_info = 'This is not image: ' + str(filepath) + '\n'
        print (err_info)
        return err_info
    try:
        if img.mode != "RGB":
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                alpha = img.convert('RGBA').split()[-1]
                arr = numpy.asarray(alpha)
                find_alpha = False
                for i in range(0, img.size[0] - 1):
                    for j in range(0, img.size[1] - 1):
                        # ？？？ 透明度较低的图片没什么用的怎么说，我这个透明度是透给谁？？？
                        if arr[j][i] < value:
                            find_alpha = True
                            break
                if not find_alpha:
                    return "RGB"
    except Exception, ex:
        print("error:" + ex.message)
        pass
    return img.mode


def check_image_limit(apk, apk_dir, limit=40000):
    count = 0
    for parent, dir_names, filenames in os.walk(apk_dir):
        for filename in filenames:
            # 获取文件的绝对路径
            path = os.path.join(parent, filename)

            # 过滤文件类型
            if not os.path.splitext(filename)[1] in LIMIT_IMAGE_FORMAT:
                continue

            # 判断文件存在
            if not filename:
                continue

            file_size = utils.get_path_size(path)
            if long(file_size) > long(limit):
                image_path = utils.get_folder_name(parent, apk_dir) + os.sep + filename
                print('IMAGE:%s  size:%s' % (image_path, utils.get_size_in_nice_string(file_size)))
                count += 1
    if count > 0:
        print("These files may be too large.(larger than %s)" % utils.get_size_in_nice_string(int(limit)))


def check_apk_alpha(apk, apk_dir, ignore9, value=255):
    # 遍历要扫描的文件夹s
    count = 0
    # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    for parent, dir_names, filenames in os.walk(apk_dir):
        for filename in filenames:
            # 获取文件的绝对路径
            path = os.path.join(parent, filename)

            # 过滤文件类型
            if not os.path.splitext(filename)[1] in ALPHA_IMAGE_FORMAT:
                continue

            # 判断文件存在
            if not filename:
                continue
            # 过滤.9
            if ignore9 and ".9" in filename:
                continue

            # 检查文件类型
            mode = check_img_mode(path, value)
            if mode == 'RGB':
                image_path = utils.get_folder_name(parent, apk_dir) + os.sep + filename
                print ('IMAGE:' + image_path)
                count += 1

    if count > 0:
        print('These %s image(s) may be pngs with no alpha, considering jpeg?' % count)


def apk_image_check(check_alpha=True, limit=40000, apk=None, ignore9=True, value=255):
    if apk is None:
        print("invalid apk file or name")
        exit()

    print("apk:" + apk)

    # 获取没有拓展名的文件名
    apk_dir = os.path.split(apk)[-1].split(".")[0]


    # 解压文件夹以便分析
    print("start to unzip apk")
    utils.surely_rmdir(apk_dir)
    utils.unzip_dir(apk, apk_dir)

    if limit is not None:
        print("")
        print("============ check size limit ==================")
        check_image_limit(apk, apk_dir, limit)
        print("============ check size limit ==================")

    if check_alpha:
        print("")
        print("")
        print("============ check image alpha ==================")
        check_apk_alpha(apk, apk_dir, ignore9, value)
        print("============ check image alpha ==================")
    print("")

    # 移除分析用的解压出来的文件
    utils.surely_rmdir(apk_dir)


def usage():
    print '------------apkimagecheck.py usage:------------'
    print '-h, --help     : print help message.'
    print '-f, --file     : apk file'
    print '-a, --alpha    : not 0 (default)-> not check pic with no alpha; 0 -> check'
    print '-v, --value    : alpha check value, default 255(check pic without even a little alpha)'
    print '-l, --limit    : file size limit in byte (1024 -> 1K)'
    print '-i, --ignore9  : not 0 (default)-> ignore .9; 0 -> check .9'
    print '----------------------------------------'


def exit():
    usage()
    print("")
    sys.exit(1)


if "__main__" == __name__:
    check_alpha = True
    limit = 40000
    apk = None
    ignore9 = True
    value = 255
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:a:l:f:i:v:", ["help", "output="])

        # print("============ opts ==================");
        # print(opts);
        #
        # print("============ args ==================");
        # print(args);

        # check all param
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                exit()
            if opt in ("-l", "--limit"):
                limit = arg
            if opt in ("-a", "--alpha"):
                check_alpha = (arg == "0")
            if opt in ("-i", "--ignore9"):
                ignore9 = (arg == "0")
            if opt in ("-f", "--file"):
                apk = arg
            if opt in ("-v", "--value"):
                alpha_value = int(arg)
                if 255 >= alpha_value >= 0:
                    value = alpha_value

    except getopt.GetoptError, e:
        print("getopt error! " + e.msg)
        exit()

    print("")
    apk_image_check(check_alpha, limit, apk, ignore9, value)
    print("")
