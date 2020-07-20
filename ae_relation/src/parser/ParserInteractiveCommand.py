#-*- coding:utf-8 -*-

from parser.ParserCommandLine import *
from parser.CommandPackage import *
from pipe.Pipe import *

class ParserInteractiveCommand(object):
    # 1. 如果开头是"!"，解析。
    # 2. 其他，传递到其他的Parser执行！

    def __init__(self, model):  #TODO: model是临时的。
        super(ParserInteractiveCommand, self).__init__()
        self.parserCommandLine = ParserCommandLine(model)
    
    def parse(self, str_action):
        # 分析和执行action.
        # return: Return: 

        cmdPkgs = []
        
        # "!" 开头的是针对此层的操作，比如对 Container 的。
        if str_action.startswith('!'):
            self._inner_parse(cmdPkgs, str_action[1:])
        else:
            #executor.do(str_action.strip())
            pkgs = self.parserCommandLine.parse(str_action.strip())
            cmdPkgs.extend(pkgs)

        return cmdPkgs

    def show_help(self):    # TODO: 多个parser时如何显示帮助信息?
        # 显示帮助信息。
        print 'command:'
        print '!help: show help information.'
        print '!quit: quit from parser.'
        print '!test: test parser.'
        
        self.parserCommandLine.show_help()

    def _inner_parse(self, cmdPkgs, str_action):
        # 解析命令，变成command package。
        # TODO 命令解析用 getopt，这样就允许用参数了。
        pkg = None

        if len(str_action) == 0:
            pass
        elif str_action.startswith("#"):
            pass
        elif str_action == 'quit':
            #return Return.QUIT
            pkg = CommandPackage(CommandId.QUIT_PIPE)
        elif str_action == 'help':
            pkg = CommandPackage(CommandId.HELP_PIPE)
        else:
            logging.error("Unknown parser command:%s" % str_action)
        
        if pkg:
            cmdPkgs.append(pkg)

        return