#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt, shutil, traceback
from Control import *
from Model import *

#######################################
## Main Entry of program.

def main(argv):
    control = Control()
    model = Model()
    control.main(argv, model)

if __name__ == '__main__':    
    main(sys.argv)
