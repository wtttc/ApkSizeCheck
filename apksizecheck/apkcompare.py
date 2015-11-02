#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import functools
import os
import sys
import getopt
import struct

import utils

__author__ = 'tiantong'

OLD_FOLDER_NAME = "old"
NEW_FOLDER_NAME = "new"
SINGLE_FOLDER_NAME = "single"


# 打开文件
def open_read_file():
    def decorator(func):
        @functools.wraps(func)
        def wrapper(file_dir):
            try:
                input_file = file(r'' + file_dir)
                f = json.load(input_file)
                input_file.close()
                return f
            except Exception, e:
                print e
                exit()

        return wrapper

    return decorator


# 从文件中获取文本
@open_read_file()
def get_json_from_file(file_dir):
    pass


# 获取文件中(jar or dex)的方法数
def get_method_counts_in_file(filepath):
    if not os.path.isfile(filepath):
        return None
    if ".jar" in filepath:
        abspath = os.path.abspath(filepath)
        # print("abspath:" + abspath)
        filename = os.path.basename(filepath).split(".")[0]
        # print("filename:" + filename)
        floderpath = os.path.split(abspath)[0]
        # print("floderpath:" + floderpath)
        unzippath = os.path.join(floderpath, filename)
        # print("unzippath:" + unzippath)
        utils.unzip_dir(abspath, unzippath)
        dexpath = os.path.join(unzippath, "classes.dex")
        count = get_method_count(dexpath)
        utils.surely_rmdir(unzippath)
        return count
    elif ".dex" in filepath:
        abspath = os.path.abspath(filepath)
        return get_method_count(abspath)
    return None


# 获取dex中得方法数
# from https://gist.github.com/jensck/4532039
def get_method_count(dex_path):
    with open(dex_path, 'rb') as dex:
        # read 88 bytes in, plus the 4 bytes for the actual integer data we want
        dex.seek(88)
        method_count_bytes = dex.read(4)
    return struct.unpack('<I', method_count_bytes)[0]


def walk_dict(parent, jdict, size_dict=None, method_dict=None, root_name=None):
    for (d, x) in jdict.items():
        path = os.path.join(parent, d)
        size = utils.get_path_size(path)
        key = d
        if root_name is not None:
            key = utils.get_folder_name(path, root_name)
        # print("key:" + key)
        if size_dict is not None and isinstance(size_dict, dict):
            size_dict[key] = size

        count = None
        if method_dict is not None:
            count = get_method_counts_in_file(path)
            if count is not None:
                # print("d:" + d + " count:" + count)
                method_dict[key] = count
        method_count = "method:"
        if count is None:
            method_count = ""
        else:
            method_count += str(count)
        print("path:%-60s | size: %-12s | %-17s" % (
            key, utils.get_size_in_nice_string(size), method_count))
        if isinstance(x, dict):
            walk_dict(path, x, size_dict, method_dict, root_name)
        else:
            pass


def compare_dict(new_apk_obj, old_apk_obj, new_method_dict, old_method_dict):
    for (k, v) in new_apk_obj.items():
        # print("k:%s  v:%s" % (k, str(v)))
        if old_apk_obj.has_key(k):
            changed = v - old_apk_obj[k]

            if new_method_dict.has_key(k):
                new_method_count = new_method_dict[k]
                old_method_count = 0
                if old_method_dict.has_key(k):
                    old_method_count = old_method_dict[k]
                method_count = new_method_count - old_method_count
                print("file:%-60s | old: %-12s | new: %-12s | changed: %-12s | methods changed:  %-12s" % (
                    k, utils.get_size_in_nice_string(old_apk_obj[k]), utils.get_size_in_nice_string(v),
                    utils.get_size_in_nice_string(changed),
                    str(method_count)))
            else:
                print("file:%-60s | old: %-12s | new: %-12s | changed: %-12s" % (
                    k, utils.get_size_in_nice_string(old_apk_obj[k]), utils.get_size_in_nice_string(v),
                    utils.get_size_in_nice_string(changed)))


def dirCompare(old_path, new_path, new_dict, removed_dict, changed_dict):
    afiles = []
    bfiles = []
    for root, dirs, files in os.walk(old_path):
        for f in files:
            afiles.append(root + os.sep + f)
    for root, dirs, files in os.walk(new_path):
        for f in files:
            bfiles.append(root + os.sep + f)

    apathlen = len(old_path)
    aafiles = []
    for f in afiles:
        aafiles.append(f[apathlen:])
    # 去掉afiles中文件名的apath
    bpathlen = len(new_path)
    bbfiles = []
    for f in bfiles:
        bbfiles.append(f[bpathlen:])
    afiles = aafiles
    bfiles = bbfiles
    setA = set(afiles)
    setB = set(bfiles)
    # 处理共有文件
    commonfiles = setA & setB
    for of in sorted(commonfiles):
        size_changed = utils.get_path_size(str(new_path + of)) - utils.get_path_size(str(old_path + of))
        if size_changed != 0:
            changed_dict[of] = size_changed

    # 处理仅出现在一个目录中的文件
    onlyFiles = setA ^ setB
    aonlyFiles = []
    bonlyFiles = []
    for of in onlyFiles:
        if of in afiles:
            aonlyFiles.append(of)
        elif of in bfiles:
            bonlyFiles.append(of)

    # print "#only in ", old_path
    for of in sorted(aonlyFiles):
        removed_dict[of] = utils.get_path_size(str(old_path + of))

    # print "#only in ", new_path
    for of in sorted(bonlyFiles):
        # print of + " size:" + get_size_in_nice_string(get_path_size(str(new_path + of)))
        new_dict[of] = utils.get_path_size(str(new_path + of))


def print_top_dict(top_dict=dict(), top=None, dict_name=""):
    top_dict = sorted(top_dict.items(), key=lambda dict: dict[1], reverse=True)
    count = 0
    if top is not None:
        print("============top %s in %s ============" % (str(top), dict_name))
    else:
        print("============%s============" % dict_name)
    for kv in top_dict:
        if top is not None and int(count) > int(top):
            break
        count += 1
        print("file:%-60s | size: %-12s " % (kv[0], utils.get_size_in_nice_string(kv[1])))


def check_unzipped_apk(apk_name, apk_path):
    file_count = sum([len(x) for _, _, x in os.walk(apk_path)])
    floder_size = utils.get_size_in_nice_string(utils.get_path_size(apk_path))
    print("apk:%s   size: %s   files: %s" % (apk_name, floder_size, file_count))


def compare_apk(apk_old, apk_new, top=None):
    # 获取没有拓展名的文件名
    old_apk_dir = os.path.join(os.path.dirname(apk_old), OLD_FOLDER_NAME)
    new_apk_dir = os.path.join(os.path.dirname(apk_old), NEW_FOLDER_NAME)
    print("old_apk_dir:" + old_apk_dir)
    print("new_apk_dir:" + new_apk_dir)

    old_size = utils.get_path_size(apk_old)
    new_size = utils.get_path_size(apk_new)
    print("apk_old:%s size: %s" % (apk_old, utils.get_size_in_nice_string(old_size)))
    print("apk_new:%s size: %s" % (apk_new, utils.get_size_in_nice_string(new_size)))
    print("")

    # 解压文件夹以便分析
    utils.surely_rmdir(old_apk_dir)
    utils.surely_rmdir(new_apk_dir)
    print("start to unzip apk old")
    utils.unzip_dir(apk_old, old_apk_dir)
    print("start to unzip apk new")
    utils.unzip_dir(apk_new, new_apk_dir)
    print("")

    print("unzip apk info:")
    check_unzipped_apk(apk_old, old_apk_dir)
    check_unzipped_apk(apk_new, new_apk_dir)

    json_object = get_json_from_file("apk_tree")
    data_string = json.dumps(json_object)
    jdict = json.loads(data_string)

    # 键值对保存要查文件的大小，用于后面对比
    old_apk_obj = dict()
    new_apk_obj = dict()
    # 方法数dict
    new_method_dict = dict()
    old_method_dict = dict()

    print("")
    print("")
    # 输出其中指定文件的大小
    print("============old==============")
    walk_dict(old_apk_dir, jdict, old_apk_obj, old_method_dict, OLD_FOLDER_NAME)
    print("============old==============")
    print("")
    print("")
    print("============new==============")
    walk_dict(new_apk_dir, jdict, new_apk_obj, new_method_dict, NEW_FOLDER_NAME)
    print("============new==============")
    print("")
    print("")

    print("============compare result==============")
    # compare
    compare_dict(new_apk_obj, old_apk_obj, new_method_dict, old_method_dict)
    print("============compare result==============")
    print("")
    print("")

    # 检查出apk种新添的文件
    # 文件dict，用于检查新文件
    new_file_dict = dict()
    removed_file_dict = dict()
    changed_file_dict = dict()
    dirCompare(old_apk_dir, new_apk_dir, new_file_dict, removed_file_dict, changed_file_dict)
    print_top_dict(new_file_dict, top, "new file")
    print("")
    print("")
    print_top_dict(removed_file_dict, top, "removed file")
    print("")
    print("")
    print_top_dict(changed_file_dict, top, "changed file")

    # 清除临时解压的apk文件夹
    utils.surely_rmdir(old_apk_dir)
    utils.surely_rmdir(new_apk_dir)


def get_apk_data(apk_single):
    # 获取没有拓展名的文件名
    apk_dir = os.path.join(os.path.dirname(apk_single), SINGLE_FOLDER_NAME)

    apk_size = utils.get_path_size(apk_single)
    print("apk_single:%s size: %s" % (apk_dir, utils.get_size_in_nice_string(apk_size)))

    # 解压文件夹以便分析
    print("start to unzip apk single")
    utils.surely_rmdir(apk_dir)
    utils.unzip_dir(apk_single, apk_dir)

    print("unzip apk info:")
    check_unzipped_apk(apk_single, apk_dir)

    json_object = get_json_from_file("apk_tree")
    data_string = json.dumps(json_object)
    jdict = json.loads(data_string)

    # 键值对保存要查文件的大小，用于后面对比
    apk_obj = dict()
    method_dict = dict()

    print("")
    print("")
    # 输出其中指定文件的大小
    print("============single==============")
    walk_dict(apk_dir, jdict, apk_obj, method_dict, SINGLE_FOLDER_NAME)
    print("============single==============")

    # 清除临时解压的apk文件夹
    utils.surely_rmdir(apk_dir)


def usage():
    print '------------apkcompare.py usage:------------'
    print '-h, --help     : print help message.'
    print '-o, --old      : input old apk file path'
    print '-n, --new      : input new apk file path'
    print '-s, --single   : input single apk file path, conflict with -o & -n'
    print '-t, --top      : show the top "n" file new/removed/changed in apk'
    print '----------------------------------------'


def exit():
    usage()
    sys.exit(1)


if "__main__" == __name__:
    apk_old = None
    apk_new = None
    apk_single = None
    top = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:n:s:t:", ["help", "output="])

        # print("============ opts ==================");
        # print(opts);
        #
        # print("============ args ==================");
        # print(args);

        # check all param
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                exit()
            if opt in ("-s", "--single"):
                apk_single = arg
            if opt in ("-o", "--old"):
                apk_old = arg
            if opt in ("-n", "--new"):
                apk_new = arg
            if opt in ("-t", "--top"):
                top = arg

    except getopt.GetoptError, e:
        print("getopt error! " + e.msg)
        exit()

    if apk_single is not None:
        print("apk_single valid, -o and -n will be ignored")
        # 检查单个
        get_apk_data(apk_single)
    elif apk_new is None or apk_old is None:
        print("invalid input! Able to check if valid args with -o and -n or -s")
        exit()
    else:
        compare_apk(apk_old, apk_new, top)
