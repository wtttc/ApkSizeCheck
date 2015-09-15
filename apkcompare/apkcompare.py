#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import functools
import os
import sys
import zipfile
import shutil
import getopt

__author__ = 'tiantong'


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


# 转换大小显示
def get_size_in_nice_string(sizeInBytes):
    for (cutoff, label) in [(1024 * 1024 * 1024, "GB"),
                            (1024 * 1024, "MB"),
                            (1024, "KB"),
                            ]:
        if sizeInBytes >= cutoff:
            return "%.1f %s" % (sizeInBytes * 1.0 / cutoff, label)

    if sizeInBytes == 1:
        return "1 byte"
    else:
        bytes = "%.1f" % (sizeInBytes or 0,)
        return (bytes[:-2] if bytes.endswith('.0') else bytes) + ' bytes'


# 获取文件或者文件夹大小
def get_path_size(strPath):
    if not os.path.exists(strPath):
        return 0;

    if os.path.isfile(strPath):
        return os.path.getsize(strPath);

    nTotalSize = 0;
    for strRoot, lsDir, lsFiles in os.walk(strPath):
        # get child directory size
        for strDir in lsDir:
            nTotalSize = nTotalSize + get_path_size(os.path.join(strRoot, strDir));

            # for child file size
        for strFile in lsFiles:
            nTotalSize = nTotalSize + os.path.getsize(os.path.join(strRoot, strFile));

    return nTotalSize;


# 覆盖解压缩文件
def unzip_dir(zipfilename, unzipdirname):
    fullzipfilename = os.path.abspath(zipfilename)
    fullunzipdirname = os.path.abspath(unzipdirname)
    print "Start to unzip file %s to folder %s ..." % (zipfilename, unzipdirname)
    if not os.path.exists(fullunzipdirname):
        os.mkdir(fullunzipdirname)

    srcZip = zipfile.ZipFile(fullzipfilename, "r")
    for eachfile in srcZip.namelist():
        # print "Unzip file %s ..." % eachfile
        eachfilename = os.path.normpath(os.path.join(fullunzipdirname, eachfile))
        eachdirname = os.path.dirname(eachfilename)
        if not os.path.exists(eachdirname):
            os.makedirs(eachdirname)
        fd = open(eachfilename, "wb")
        fd.write(srcZip.read(eachfile))
        fd.close()
    srcZip.close()
    print "Unzip file succeed!"


def walk_dict(parent, jdict, obj=None):
    for (d, x) in jdict.items():
        path = os.path.join(parent, d)
        size = get_path_size(path)
        if obj is not None and isinstance(obj, dict):
            obj[d] = size
        print "path:" + path + "    size:" + get_size_in_nice_string(size)
        if isinstance(x, dict):
            walk_dict(path, x, obj)
        else:
            pass


def surely_rmdir(dir):
    if os.path.exists(dir) and os.path.isdir(dir):
        shutil.rmtree(dir)


def compare_apk(apk_old, apk_new):
    # 获取没有拓展名的文件名
    old_apk_dir = os.path.split(apk_old)[-1].split(".")[0]
    new_apk_dir = os.path.split(apk_new)[-1].split(".")[0]

    old_size = get_path_size(apk_old)
    new_size = get_path_size(apk_new)
    print("apk_old:" + apk_old + " size:" + get_size_in_nice_string(old_size))
    print("apk_new:" + apk_new + " size:" + get_size_in_nice_string(new_size))

    # 解压文件夹以便分析
    surely_rmdir(old_apk_dir)
    surely_rmdir(new_apk_dir)
    unzip_dir(apk_old, old_apk_dir)
    unzip_dir(apk_new, new_apk_dir)
    json_object = get_json_from_file("apk_tree");
    data_string = json.dumps(json_object)
    jdict = json.loads(data_string)

    # 键值对保存要查文件的大小，用于后面对比
    old_apk_obj = dict();
    new_apk_obj = dict();

    print("")
    print("")
    # 输出其中指定文件的大小
    print("============%s==============" % old_apk_dir)
    walk_dict(old_apk_dir, jdict, old_apk_obj)
    print("============%s==============" % old_apk_dir)
    print("")
    print("")
    print("============%s==============" % new_apk_dir)
    walk_dict(new_apk_dir, jdict, new_apk_obj)
    print("============%s==============" % new_apk_dir)
    print("")
    print("")

    print("============compare result==============")
    # compare
    for (k, v) in new_apk_obj.items():
        # print("k:%s  v:%s" % (k, str(v)))
        if old_apk_obj.has_key(k):
            changed = v - old_apk_obj[k]
            deltaString = ""
            if changed < 0:
                changed = -changed
                deltaString = "-" + get_size_in_nice_string(changed)
            else:
                deltaString = get_size_in_nice_string(changed)

            print("file:%s has changed %s" % (k, deltaString))
    print("============compare result==============")
    print("")
    print("")

    # 清除临时解压的apk文件夹
    surely_rmdir(old_apk_dir)
    surely_rmdir(new_apk_dir)


def usage():
    print '------------PyTest.py usage:------------'
    print '-h, --help: print help message.'
    print '-o, --old : input old apk file path'
    print '-n, --new : input new apk file path'
    print '----------------------------------------'


if "__main__" == __name__:
    apk_old = None;
    apk_new = None;
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:n:", ["help", "output="])

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
            if opt in ("-o", "--old"):
                apk_old = arg
            if opt in ("-n", "--new"):
                apk_new = arg

    except getopt.GetoptError:
        print("getopt error!");
        usage();
        sys.exit(1);

    if apk_new is None or apk_old is None:
        print("invalid input! Able to check if valid args with -o and -n");
        usage();
        sys.exit(1);

    compare_apk(apk_old, apk_new)
