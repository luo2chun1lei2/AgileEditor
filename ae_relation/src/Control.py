# -*- coding:utf-8 -*-
# 控制所有的模块，以及单独的模块。
# 1. 接受外部的操控，包括命令输入、鼠标输入等。
# 1. 控制所有的模块，以及各个子模块。
# 1. Control不需要知道每个模块的具体含义。



from Model import *

def program_usage():
    # 和 PROGRAM_CMD 一致
    print 'program usage:'
    print 'help: show help information.'
    print 'script <script file path>: run input script'

def control_usage():
    # 和 CMDLINE_CMD 一致。
    print 'control usage:'
    print 'help: show help information.'
    print 'quit: quit from control.'
    print 'test: test this program.'
    print 'select: select on element and do something to it.'
    print 'insert: insert element.'
    print 'update: update properties of element.'
    print 'delete: delete element or relation.'
    print 'drop: drop all data.'
    

# TODO 目前还用不到。
class SystemCommand(object):
    # 系统级别的命令。
    # 命令是解析好的“描述如何执行的数据”，和普通的命令相比，不适用于人类阅读的，而是用于方便执行的。
    def __self__(self):
        super(SystemCommand, self).__init__()

class Control(object):
    
    def __init__(self):
        super(Control, self).__init__()
    
    def do(self, model, str_action):
        # 执行action
        # model: Model: control对应的模型
        # str_action: Action: 做的动作，以字符串格式

        argv = str_action.split()
        if argv[0] == "help":
            self._help()
        elif argv[0] == "script":
            opts, args = self._parse_one_action(argv[1:], "l", ["list"])
            logging.error(opts)
            logging.error(args)
            
        else:
            print "Unknown MVC command:%s" % argv[0]
            self._help()
        
        # 目前Control无法退出程序，只能执行命令。
        return True

    def _help(self):
        print 'mvc usage:'
        print 'help: show help information.'
        print 'script -l <path>: load script.'

    def _parse_one_action(self, argv, short_args, long_args):
        try:
            opts, args = getopt.getopt(argv, short_args, long_args)
        except getopt.GetoptError, err:
            print str(err)
            self._help()
            return (None, None)
        
        return (opts, args)
    