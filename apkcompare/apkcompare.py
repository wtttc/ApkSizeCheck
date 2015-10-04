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
    # print "Start to unzip file %s to folder %s ..." % (zipfilename, unzipdirname)
    # Check input ...
    if not os.path.exists(fullzipfilename):
        print "Dir/File %s is not exist, Press any key to quit..." % fullzipfilename
        inputStr = raw_input()
        return
    if not os.path.exists(fullunzipdirname):
        os.mkdir(fullunzipdirname)
    else:
        if os.path.isfile(fullunzipdirname):
            print "File %s is exist, are you sure to delet it first ? [Y/N]" % fullunzipdirname
            while 1:
                inputStr = raw_input()
                if inputStr == "N" or inputStr == "n":
                    return
                else:
                    if inputStr == "Y" or inputStr == "y":
                        os.remove(fullunzipdirname)
                        print "Continue to unzip files ..."
                        break

    # Start extract files ...
    srcZip = zipfile.ZipFile(fullzipfilename, "r")
    for eachfile in srcZip.namelist():
        try:
            # print "Unzip file %s ..." % eachfile
            eachfilename = os.path.normpath(os.path.join(fullunzipdirname, eachfile))
            eachdirname = os.path.dirname(eachfilename)
            if not os.path.exists(eachdirname):
                os.makedirs(eachdirname)
            fd = open(eachfilename, "wb")
            fd.write(srcZip.read(eachfile))
            fd.close()
        except Exception,e:
            pass
    srcZip.close()
    # print "Unzip file succeed!"


# 使用命令行解压
def unzip_with_command(jar_path, out_path):
    command = 'unzip ' + jar_path + ' -d ' + out_path
    result = os.popen(command).read()


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
        unzip_dir(abspath, unzippath)
        dexpath = os.path.join(unzippath, "classes.dex")
        count = get_method_count(dexpath)
        surely_rmdir(unzippath)
        return count
    elif ".dex" in filepath:
        abspath = os.path.abspath(filepath)
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


# 获取dex中得方法数
# from https://gist.github.com/jensck/4532039
def get_method_count(dex_path):
    with open(dex_path, 'rb') as dex:
        # read 88 bytes in, plus the 4 bytes for the actual integer data we want
        dex.seek(88)
        method_count_bytes = dex.read(4)
    return struct.unpack('<I', method_count_bytes)[0]


def get_folder_name(parent, floder_root):
    # 默认情况显示最后一个文件夹的名字
    if floder_root is not None and floder_root not in parent:
        _list = parent.split(os.sep)
        if _list[-1].__len__() > 0:
            return _list[-1]
        return _list[-2]

    folder_name = os.path.split(parent)
    if folder_name[1] == floder_root:
        return folder_name[1].replace(floder_root, "")
    else:
        return get_folder_name(folder_name[0], floder_root) + os.sep + folder_name[1]


def walk_dict(parent, jdict, size_dict=None, method_dict=None, root_name=None):
    for (d, x) in jdict.items():
        path = os.path.join(parent, d)
        size = get_path_size(path)
        key = d
        if root_name is not None:
            key = get_folder_name(path, root_name)
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
        print("path:%-30s | size: %-12s | %-17s" % (
            key, get_size_in_nice_string(size), method_count))
        if isinstance(x, dict):
            walk_dict(path, x, size_dict, method_dict, root_name)
        else:
            pass


def surely_rmdir(dir):
    if os.path.exists(dir) and os.path.isdir(dir):
        shutil.rmtree(dir)


def compare_dict(new_apk_obj, old_apk_obj, new_method_dict, old_method_dict):
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
                new_method_count = new_method_dict[k]
                old_method_count = 0
                if old_method_dict.has_key(k):
                    old_method_count = old_method_dict[k]
                method_count = new_method_count - old_method_count
                print("file:%-30s | old: %-12s | new: %-12s | changed: %-12s | methods changed:  %-12s" % (
                    k, get_size_in_nice_string(old_apk_obj[k]), get_size_in_nice_string(v), deltaString,
                    str(method_count)))
            else:
                print("file:%-30s | old: %-12s | new: %-12s | changed: %-12s" % (
                    k, get_size_in_nice_string(old_apk_obj[k]), get_size_in_nice_string(v), deltaString))


def dirCompare(old_path, new_path, new_dict):
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
    # commonfiles = setA & setB
    # print "#================================="
    # print "common in '", apath, "' and '", bpath, "'"
    # print "#================================="
    # print '\t\t\ta:\t\t\t\t\t\tb:'
    # for f in sorted(commonfiles):
    #     print f + "\t\t" + getPrettyTime(os.stat(apath + "\\" + f)) + "\t\t" + getPrettyTime(os.stat(new_path + "\\" + f))

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
    # for of in sorted(aonlyFiles):
    #     print of

    # print "#only in ", new_path
    for of in sorted(bonlyFiles):
        # print of + " size:" + get_size_in_nice_string(get_path_size(str(new_path + of)))
        new_dict[of] = get_path_size(str(new_path + of))


def compare_apk(apk_old, apk_new, top_count=None):
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
    print("start to unzip apk old")
    unzip_dir(apk_old, old_apk_dir)
    print("start to unzip apk new")
    unzip_dir(apk_new, new_apk_dir)
    json_object = get_json_from_file("apk_tree");
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
    print("============%s==============" % old_apk_dir)
    walk_dict(old_apk_dir, jdict, old_apk_obj, old_method_dict, old_apk_dir)
    print("============%s==============" % old_apk_dir)
    print("")
    print("")
    print("============%s==============" % new_apk_dir)
    walk_dict(new_apk_dir, jdict, new_apk_obj, new_method_dict, new_apk_dir)
    print("============%s==============" % new_apk_dir)
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
    dirCompare(old_apk_dir, new_apk_dir, new_file_dict)
    sorted_list = sorted(new_file_dict.items(), key=lambda new_file_dict: new_file_dict[1], reverse=True)
    count = 0
    if top_count is not None:
        print("============top " + str(top_count) + " large new file============")
    else:
        print("============new file============")
    for kv in sorted_list:
        if top_count is not None and int(count) > int(top_count):
            break
        count += 1
        print("file:%-60s | size: %-12s " % (kv[0], get_size_in_nice_string(kv[1])))



    # 清除临时解压的apk文件夹
    surely_rmdir(old_apk_dir)
    surely_rmdir(new_apk_dir)


def get_apk_data(apk_single):
    # 获取没有拓展名的文件名
    apk_dir = os.path.split(apk_single)[-1].split(".")[0]

    apk_size = get_path_size(apk_single)
    print("apk_single:" + apk_dir + " size:" + get_size_in_nice_string(apk_size))

    # 解压文件夹以便分析
    surely_rmdir(apk_dir)
    unzip_dir(apk_single, apk_dir)
    json_object = get_json_from_file("apk_tree");
    data_string = json.dumps(json_object)
    jdict = json.loads(data_string)

    # 键值对保存要查文件的大小，用于后面对比
    apk_obj = dict();
    method_dict = dict();

    print("")
    print("")
    # 输出其中指定文件的大小
    print("============%s==============" % apk_dir)
    walk_dict(apk_dir, jdict, apk_obj, method_dict, apk_dir)
    print("============%s==============" % apk_dir)

    # 清除临时解压的apk文件夹
    surely_rmdir(apk_dir)


def usage():
    print '------------PyTest.py usage:------------'
    print '-h, --help   : print help message.'
    print '-o, --old    : input old apk file path'
    print '-n, --new    : input new apk file path'
    print '-s, --single : input single apk file path, conflict with -o & -n'
    print '----------------------------------------'


if "__main__" == __name__:
    apk_old = None;
    apk_new = None;
    apk_single = None;
    top_count = None;
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
                usage();
                sys.exit(1);
            if opt in ("-s", "--single"):
                apk_single = arg
            if opt in ("-o", "--old"):
                apk_old = arg
            if opt in ("-n", "--new"):
                apk_new = arg
            if opt in ("-t", "--topcount"):
                top_count = arg


    except getopt.GetoptError, e:
        print("getopt error! " + e.msg);
        usage();
        sys.exit(1);

    if apk_single is not None:
        print("apk_single valid, -o and -n will be ignored");
        # 检查单个
        get_apk_data(apk_single)
    elif apk_new is None or apk_old is None:
        print("invalid input! Able to check if valid args with -o and -n or -s");
        usage();
        sys.exit(1);
    else:
        compare_apk(apk_old, apk_new, top_count)
