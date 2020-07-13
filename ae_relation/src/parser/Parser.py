#-*- coding:utf-8 -*-

# Parser模块：
# 1. 解析传入的命令，不关心命令来自于GUI/CUI/File什么，
# 2. 如果开头是"!"，那么就是针对parser的，
# 3. 其他，则以字符串的方式传入到 MVC:Controller中去执行。

from parser.Control import *
from pipe.Pipe import *

class Parser():
    def __init__(self, container):
        self.container = container
    
    def do(self, str_action):
        # 分析和执行action.
        # return: Return: 
        
        # "!" 开头的是针对此层的操作，比如对 Container 的。
        if str_action.startswith('!'):
            return self._inner_do(str_action[1:])
        else:
            self.container.do_action_by_current_control(str_action)
            return Return.OK

    def _help(self):
        # 显示帮助信息。
        print 'parser usage:'
        print 'help: show help information.'
        print 'quit: quit from parser.'
        print 'test: test parser.'
        
    def _test_self(self):
        # TODO: 这里需要吗？
        print "NOT IMPLEMENT."

    def _inner_do(self, str_action):
        # str_action: String: 命令以字符串的方式传入
        # 执行Parser内部的命令，这些命令主要是针对Container。
        logging.debug("Execute inner command:%s" % str_action)

        # TODO 命令解析用 getopt，这样就允许用参数了。
        if len(str_action) == 0:
            pass
        elif str_action.startswith("#"):
            pass
        elif str_action == 'quit':
            return Return.QUIT
        elif str_action == 'help':
            self._help()
        elif str_action == 'test':
            self._test_self()
        else:
            print "Unknown parser command:%s" % str_action
            
        return Return.OK