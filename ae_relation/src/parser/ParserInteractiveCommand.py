#-*- coding:utf-8 -*-

import logging

from misc import *
from parser.Parser import *
from parser.CommandPackage import *
from processor.Processor import *

class ParserInteractiveCommand(Parser):
    # 1. 如果开头是"!"，解析。
    # 2. 其他，传递到其他的Parser执行！

    def __init__(self, model):
        super(ParserInteractiveCommand, self).__init__()
        
        self.join_lines = JoinLines()
    
    def parse(self, line_no, line):
        # 分析和执行action.
        # @param line_no int 行号，不一定是连续的。
        # @param line string 一行输入。
        # return: CommandPackage[]
        
        cur_cmd = None
        # 如果行的结尾是“\”，需要等下一行再分析。
        if self.join_lines.in_join():
            cur_cmd = self.join_lines.join(line_no, line)
            if cur_cmd == None:
                return [] # 继续
        else:
            cmdPkgs = []
            
            # "!" 开头的是针对此层的操作，比如对 Container 的。
            if line.startswith('!'):
                cur_cmd = self.join_lines.join(line_no, line)
                if cur_cmd == None:
                    return [] # 继续
                
                
        if cur_cmd == None:
            # 忽略
            cmdPkgs = None
        else:
            # 分析
            self._inner_parse(cmdPkgs, cur_cmd[1:])
            
        return cmdPkgs

    def show_help(self):
        # 显示帮助信息。
        print 'Interactive commands to processor:'
        print '  !help : show help information.'
        print '  !quit : quit from processor.'
        print '  !script <file> : run script file.'

    def _inner_parse(self, cmdPkgs, str_action):
        # 解析命令，变成command package。
        # TODO: 命令解析用 getopt，这样就允许用参数了。
        pkg = None

        if len(str_action) == 0:
            pass
        elif str_action.startswith("#"):
            pass
        elif str_action == 'quit':
            pkg = CommandPackage(CommandId.QUIT_PROCESSOR)
        elif str_action == 'help':
            pkg = CommandPackage(CommandId.HELP_PROCESSOR)
        else:
            logging.error("Unknown parser command:%s" % str_action)
        
        if pkg:
            cmdPkgs.append(pkg)

        return