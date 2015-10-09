#! /usr/bin/env python
# -*- coding: utf-8 -*-
import getopt
import sys

__author__ = 'tiantong'


def usage():
    print '------------apkimagecheck.py usage:------------'
    print '-h, --help     : print help message.'
    print '-a, --alpha    : not 0 (default)-> not check pic with no alpha; 0 -> check'
    print '-l, --limit    : file size limit in byte (1024 -> 1K)'
    print '----------------------------------------'


def exit():
    usage()
    sys.exit(1)


if "__main__" == __name__:
    check_alpha = False
    limit = None;
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:a:l:", ["help", "output="])

        print("============ opts ==================");
        print(opts);

        print("============ args ==================");
        print(args);

        # check all param
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                usage();
                sys.exit(1);
            if opt in ("-l", "--limit"):
                limit = arg
            if opt in ("-a", "--alpha"):
                check_alpha = (arg == "0")

    except getopt.GetoptError, e:
        print("getopt error! " + e.msg);
        exit()

    if limit is not None:
        print("limit " + str(limit));
        # check_limit()
    if check_alpha:
        print("check_alpha " + str(check_alpha));
        # check_alpha()
