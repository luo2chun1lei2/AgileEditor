#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt, shutil, traceback
from app.App import *

#######################################
## 程序的主要入口。
## 主要是启动App。

def main(argv):
    PATH_THIS_FILE = os.path.abspath(__file__)
    util_set_exe_dir(os.path.dirname(os.path.dirname(PATH_THIS_FILE)))

    app = App()
    app.do(argv)

if __name__ == '__main__':
    main(sys.argv)
