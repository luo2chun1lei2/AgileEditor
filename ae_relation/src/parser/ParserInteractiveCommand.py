#-*- coding:utf-8 -*-

from parser.Parser import *
from parser.ParserCommandLine import *
from parser.CommandPackage import *
from processor.Processor import *

class ParserInteractiveCommand(Parser):
    # 1. 如果开头是"!"，解析。
    # 2. 其他，传递到其他的Parser执行！

    def __init__(self, model):  #TODO: model是临时的。
        super(ParserInteractiveCommand, self).__init__()
        self.parserCommandLine = ParserCommandLine(model)
        
        # 最新的一行命令。
        self.cur_cmd = ""
    
    def parse(self, line_no, line):
        # 分析和执行action.
        # @param line_no int 行号，不一定是连续的。
        # @param line string 一行输入。
        # return: command package []:
        #         None: 有可能输入信息不完整，无法完成分析！
        
        # 如果行的结尾是“\”，需要等下一行再分析。
        # 输入文件类型脚本的特点，不放在parser中。
        if len(line) > 0 and line[-1] == '\\':
            self.cur_cmd += line[:-1]
            return None
        else:
            self.cur_cmd += line

        cmdPkgs = []
        
        # "!" 开头的是针对此层的操作，比如对 Container 的。
        if self.cur_cmd.startswith('!'):
            self._inner_parse(cmdPkgs, self.cur_cmd[1:])
        else:
            pkgs = self.parserCommandLine.parse(line_no, self.cur_cmd.strip())
            cmdPkgs.extend(pkgs)

        self.cur_cmd = ""
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
            pkg = CommandPackage(CommandId.QUIT_PROCESSOR)
        elif str_action == 'help':
            pkg = CommandPackage(CommandId.HELP_PROCESSOR)
        else:
            logging.error("Unknown parser command:%s" % str_action)
        
        if pkg:
            cmdPkgs.append(pkg)

        return