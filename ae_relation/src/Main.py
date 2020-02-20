#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt, shutil, traceback
from app.App import *

#######################################
## 程序的主要入口。

def main(argv):
    
    app = App()
    app.do(argv)

if __name__ == '__main__':
    main(sys.argv)
