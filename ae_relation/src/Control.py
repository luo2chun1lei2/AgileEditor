# -*- coding:utf-8 -*-
# 控制所有的模块，以及单独的模块。
# 1. 接受外部的操控，包括命令输入、鼠标输入等。
# 1. 控制所有的模块，以及各个子模块。
# 1. Control不需要知道每个模块的具体含义。

import os, sys, logging, getopt, shutil, traceback
from Model import *

def main_usage():
    print 'program usage:'
    print '-h, --help: show help information.'
    
def control_usage():
    print 'control usage:'
    print 'h/help: show help information.'
    print 'q/quit: quit from control.'

class Control(object):
    def __init__(self):
        super(Control, self).__init__()
        

    def loop(self):
        # 进入Loop循环
        
        while True:
            str = raw_input(">")
            
            if str == 'quit' or str == 'q':
                break
            if str == 'help' or str == 'h':
                control_usage()
            elif str == 'test':
                test2()
            else:
                print "unknown:%s" % str
    
    def main(self, argv):
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
                main_usage()
                sys.exit(0)
            else:
                print 'unknown arguments.'
                main_usage()
                sys.exit(2)
        
        self.loop()
        
        sys.exit(0)