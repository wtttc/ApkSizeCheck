#! /usr/bin/env python
# -*- coding: utf-8 -*-
import getopt
import os
import sys
import utils

__author__ = 'tiantong'


def estimate_target_file(apk_file, target, out_floder=None):
    # 确保输出的临时文件夹存在
    if out_floder is None:
        out_floder = utils.cur_file_dir()
    out_floder = os.path.join(out_floder, "temp")
    if not os.path.isdir(out_floder):
        os.makedirs(out_floder)

    # 获取需要检查的set文件
    search_target_set = utils.read_set_from_file(target)
    if search_target_set is None:
        exit()


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

        # print("============ opts ==================");
        # print(opts);
        #
        # print("============ args ==================");
        # print(args);

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
