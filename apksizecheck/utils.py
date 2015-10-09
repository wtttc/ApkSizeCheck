#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import zipfile
import sys
import shutil

__author__ = 'tiantong'


# 转换大小显示
def get_size_in_nice_string(sizeInBytes):
    if sizeInBytes < 0:
        return "-" + get_size_in_nice_string(-sizeInBytes)

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
        print "Dir/File %s is not exist, just quit..." % fullzipfilename
        exit()
        return
    # remove exist file or floder
    if not os.path.exists(fullunzipdirname):
        os.mkdir(fullunzipdirname)
    else:
        if os.path.isfile(fullunzipdirname):
            while 1:
                os.remove(fullunzipdirname)
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
        except Exception, e:
            pass
    srcZip.close()
    # print "Unzip file succeed!"


def check_apk_name_valid(name):
    apk_name = os.path.split(name)[-1]
    count = apk_name.count(".") + apk_name.count(" ")
    if count > 1:
        print("Find name invalid, please rename to continue.")
        sys.exit(1)


def surely_rmdir(dir):
    if os.path.exists(dir) and os.path.isdir(dir):
        shutil.rmtree(dir)


# 获取到floder_root路径文件夹的路径
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
