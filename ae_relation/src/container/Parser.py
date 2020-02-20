#-*- coding:utf-8 -*-

# Parser模块：
# 1. 解析传入的命令，不关心命令来自于GUI/CUI/File什么，
# 如果开头是！，那么就是针对parser的，
# 其他，则以字符串的方式传入到 MVC:Controller中去执行。

from Control import *
from container.Container import *

class Parser():
    def __init__(self, container):
        self.container = container
    
    def do(self, str_action):
        # 分析和执行action.
        # return: Return: 
        
        if str_action.startswith('!'):
            return self._do_inner(str_action[1:])
        else:
            return self.container.do_action_by_current_control(str_action)

    def _help(self):
        print 'parser usage:'
        print 'help: show help information.'
        print 'quit: quit from parser.'
        print 'test: test parser.'
        
    def _test_self(self):
        print "test this parser, is OK."

    def _do_inner(self, str_action):
        # str_action: String: 命令以字符串的方式传入
        # 执行Parser内部的命令。
        logging.debug("Execute inner command:%s" % str_action)
        
        
        # TODO 命令解析用 getopt。
        if len(str_action) == 0:
            pass
        elif str_action.startswith("#"):
            pass
        elif str_action == 'quit':
            return False
        elif str_action == 'help':
            self._help()
        elif str_action == 'test':
            self._test_self()
        #elif str_action == 'create class':
            # TODO: 想创建一个uml class
            #model.create_class('')
        else:
            print "Unknown parser command:%s" % str_action
            
        return True