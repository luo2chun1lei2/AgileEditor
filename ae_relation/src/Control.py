# -*- coding:utf-8 -*-
# 控制所有的模块，以及单独的模块。
# 1. 接受外部的操控，包括命令输入、鼠标输入等。
# 1. 控制所有的模块，以及各个子模块。
# 1. Control不需要知道每个模块的具体含义。

import os, sys, logging, getopt, shutil, traceback
from Model import *

def usage():
    print 'program usage:'
    print '-h, --help: show help information.'

class Control:
    def __init__(self):
        super(Control, self).__init__()
        
    
    @staticmethod    
    def main(argv):
        logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')
        
        u''' Analysis command's arguments '''
    
        # analysis code.
        try:
            opts, args = getopt.getopt(argv[1:], 'h', ['help'])
        except getopt.GetoptError, err:
            print str(err)
            usage()
            sys.exit(1)
            
        for o, a in opts:
            if o in ('-h', '--help'):
                usage()
                sys.exit(0)
            else:
                print 'unknown arguments.'
                usage()
                sys.exit(2)
        
        test2()
        
        sys.exit(0)