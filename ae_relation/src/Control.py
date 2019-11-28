# -*- coding:utf-8 -*-
# 控制所有的模块，以及单独的模块。
# 1. 接受外部的操控，包括命令输入、鼠标输入等。
# 1. 控制所有的模块，以及各个子模块。
# 1. Control不需要知道每个模块的具体含义。

from __future__ import unicode_literals

import os, sys, logging, getopt, shutil, traceback
from Model import *

# 用于命令提示
from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

def main_usage():
    print 'program usage:'
    print 'help: show help information.'
    # TODO:
    print '...'
    
def control_usage():
    # TODO: 需要和关键字匹配
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
    
    CMDLINE_CMD = ['help', 'quit', 'test',
                    'select', 'from', 'insert', 'update', 'delete', 'drop']
    
    def __init__(self):
        super(Control, self).__init__()
        
    # TODO 目前还用不到。
    def parse_command(self, str_cmd):
        # str_cmd: String: command as string format
        return SystemCommand()
    
    def execute_command(self, model, str_cmd):
        # return: bool: if true, continue, false, break loop.
        if str_cmd == 'quit' or str_cmd == 'q':
            return False
        elif str_cmd == 'help' or str_cmd == 'h':
            control_usage()
        elif str_cmd == 'test':
            model.test2()
        elif str_cmd == 'create_class':
            # 想创建一个uml class
            model.create_class('')
        else:
            print "unknown:%s" % str_cmd
            
        return True

    def loop(self, model):
        # 进入Loop循环
        
        
        
        # 设定命令的提示符号。
        # TODO 提示的关键字，需要和下面的命令解析配套。
        word_completer = WordCompleter(Control.CMDLINE_CMD,
                                       ignore_case=True)
        
        while True:
            
            input_str = prompt('>', completer=word_completer,
                  complete_while_typing=False)

            # TODO 目前还用不到。
            #command = self.parse_command(input_str)
            
            rlt = self.execute_command(model, input_str)
            if not rlt:
                break
            
    
    def main(self, argv, model):
        # set log and level.
        logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')
        
        u''' Analysis command's arguments '''
    
        # analysis command arguments.
        # 命令分成：program command options.
        if len(argv) == 1:
            # Only this program name, goto loop.
            self.loop(model)

        elif len(argv) > 1:
            # check command is ok.
            if argv[1] not in Control.CMDLINE_CMD:
                print 'unknown command(%s).' % argv[1]
                main_usage()
                sys.exit(2)
            else:
                self.execute_command(model, " ".join(argv[1:]))

# TODO:应该是每个command，一个参数分析。
#             try:
#                 opts, args = getopt.getopt(argv[2:], 'h', ['help'])
#             except getopt.GetoptError, err:
#                 print str(err)
#                 main_usage()
#                 sys.exit(1)
#                 
#             for o, a in opts:
#                 if o in ('-h', '--help'):
#                     main_usage()
#                     sys.exit(0)
#                 else:
#                     pass

