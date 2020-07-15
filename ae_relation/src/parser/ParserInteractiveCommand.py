#-*- coding:utf-8 -*-

from parser.ParserCommandLine import *
from pipe.Pipe import *

class ParserInteractiveCommand(object):
    # 1. 如果开头是"!"，解析。
    # 2. 其他，传递到其他的Parser执行！

    def __init__(self):
        super(ParserInteractiveCommand, self).__init__()
    
    def do(self, executor, str_action):
        # 分析和执行action.
        # return: Return: 
        
        # "!" 开头的是针对此层的操作，比如对 Container 的。
        if str_action.startswith('!'):
            return self._inner_do(executor, str_action[1:])
        else:
            executor.do(str_action.strip())
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

    def _inner_do(self, executor, str_action):
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