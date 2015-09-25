#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import functools
import os
import subprocess
import sys
import zipfile
import shutil
import getopt
import struct

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


def unzip_with_command(jar_path, out_path):
    command = 'unzip ' + jar_path + ' -d ' + out_path
    result = os.popen(command).read()


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
        unzip_with_command(abspath, unzippath)
        dexpath = os.path.join(unzippath, "classes.dex")
        # return get_method_counts_in_dex(dexpath)
        return get_method_count(dexpath)
    elif ".dex" in filepath:
        abspath = os.path.abspath(filepath)
        # return get_method_counts_in_dex(abspath)
        return get_method_count(abspath)
    return None


# http://mp.weixin.qq.com/s?__biz=MzAwNDY1ODY2OQ==&amp;mid=208008519&amp;idx=1&amp;sn=278b7793699a654b51588319b15b3013&amp;scene=1&amp;srcid=0924KyxvtDNaHGrK2iL76iiH#rd
def get_method_counts_in_dex(dexpath):
    if not os.path.isfile(dexpath):
        return None
    # print("dexpath:" + dexpath)
    # command = "cat " + dexpath + " | head -c 92 | tail -c 4 | hexdump -e \'1/4 \"%d\n\"'"
    # result = os.popen(command, stdout=subprocess.PIPE, shell=True)

    # 该方法在mac上总是报错
    try:
        # p1 = subprocess.Popen('cat ' + dexpath, stdout=subprocess.PIPE, shell=True)
        # p2 = subprocess.Popen('head -c 92', stdin=p1.stdout, stdout=subprocess.PIPE, shell=True)
        # p1.stdout.close()
        # p3 = subprocess.Popen('tail -c 4', stdin=p2.stdout, stdout=subprocess.PIPE, shell=True)
        # p2.stdout.close()
        # handle = subprocess.Popen("hexdump -e \'1/4 \"%d\n\"\'", stdin=p3.stdout, stdout=subprocess.PIPE, shell=True)
        # p3.stdout.close()
        # # print handle.stdout.read()
        # return str(handle.communicate()[0])
        output = subprocess.check_output("cat " + dexpath + " | head -c 92 | tail -c 4 | hexdump -e \'1/4 \"%d\n\"\'",
                                         shell=True)
        return output
    except Exception, e:
        print("catch exception:", e)
    return None


# from https://gist.github.com/jensck/4532039
def get_method_count(dex_path):
    with open(dex_path, 'rb') as dex:
        # read 88 bytes in, plus the 4 bytes for the actual integer data we want
        dex.seek(88)
        method_count_bytes = dex.read(4)
    return struct.unpack('<I', method_count_bytes)[0]


def walk_dict(parent, jdict, size_dict=None, method_dict=None):
    for (d, x) in jdict.items():
        path = os.path.join(parent, d)
        size = get_path_size(path)
        if size_dict is not None and isinstance(size_dict, dict):
            size_dict[d] = size

        if method_dict is not None:
            count = get_method_counts_in_file(path)
            if count is not None:
                # print("d:" + d + " count:" + count)
                method_dict[d] = count
        print "path:" + path + "    size:" + get_size_in_nice_string(size)
        if isinstance(x, dict):
            walk_dict(path, x, size_dict, method_dict)
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
    new_method_dict = dict();

    print("")
    print("")
    # 输出其中指定文件的大小
    print("============%s==============" % old_apk_dir)
    walk_dict(old_apk_dir, jdict, old_apk_obj, None)
    print("============%s==============" % old_apk_dir)
    print("")
    print("")
    print("============%s==============" % new_apk_dir)
    walk_dict(new_apk_dir, jdict, new_apk_obj, new_method_dict)
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

            if new_method_dict.has_key(k):
                method_count = new_method_dict[k]
                print("file:%-20s | old: %-12s | new: %-12s | changed: %-12s | methods:  %-12s" % (
                    k, get_size_in_nice_string(old_apk_obj[k]), get_size_in_nice_string(v), deltaString, method_count))
            else:
                print("file:%-20s | old: %-12s | new: %-12s | changed: %-12s" % (
                    k, get_size_in_nice_string(old_apk_obj[k]), get_size_in_nice_string(v), deltaString))
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
