#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt, shutil, traceback
from Control import *
from mvc.model.TestModel1 import *

#######################################
## 程序的主要入口。

def main(argv):
    control = Control()
    model = TestModel1()
    control.main(argv, model)

if __name__ == '__main__':
    main(sys.argv)
