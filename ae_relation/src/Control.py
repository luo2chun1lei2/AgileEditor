# -*- coding:utf-8 -*-
# 控制所有的模块，以及单独的模块。
# 1. 接受外部的操控，包括命令输入、鼠标输入等。
# 1. 控制所有的模块，以及各个子模块。
# 1. Control不需要知道每个模块的具体含义。

from __future__ import unicode_literals

import os, sys, logging, getopt, shutil, traceback
from Model import *

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.contrib.completers import WordCompleter

def main_usage():
    print 'program usage:'
    print '-h, --help: show help information.'
    
def control_usage():
    print 'control usage:'
    print 'h/help: show help information.'
    print 'q/quit: quit from control.'
    

# TODO 目前还用不到。
class SystemCommand(object):
    # 系统级别的命令。
    # 命令是解析好的“描述如何执行的数据”，和普通的命令相比，不适用于人类阅读的，而是用于方便执行的。
    def __self__(self):
        super(SystemCommand, self).__init__()

class Control(object):
    def __init__(self):
        super(Control, self).__init__()
        
    # TODO 目前还用不到。
    def parse_command(self, str_cmd):
        # str_cmd: String: command as string format
        return SystemCommand()
        

    def loop(self):
        # 进入Loop循环
        
        model = Model()
        
        SQLCompleter = WordCompleter(['select', 'from', 'insert', 'update', 'delete', 'drop'],
                             ignore_case=True)
        
        while True:
            str = prompt('>',
                         history=FileHistory('history.txt'),
                         auto_suggest=AutoSuggestFromHistory(),
                         completer=SQLCompleter,
                       )
            
            # TODO 目前还用不到。
            #command = self.parse_command(str)
            
            if str == 'quit' or str == 'q':
                break
            elif str == 'help' or str == 'h':
                control_usage()
            elif str == 'test':
                model.test2()
            elif str == 'create_class':
                # 想创建一个uml class
                model.create_class('')
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
            main_usage()
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