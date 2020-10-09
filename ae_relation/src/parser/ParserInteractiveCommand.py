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
        print '  !processor <name> : load processor by given name.'
        print '  !script <file> : run script file(absolute path or relative to current path).'

    def _inner_parse(self, cmdPkgs, str_action):
        # 解析命令，变成command package。
        
        pkg = None
        
        if len(str_action) == 0:
            pass
        elif str_action.startswith("#"):
            pass
        
        # TODO 这里有一个严重的问题，就是script、processor执行的都是AppExecutor的命令，
        # 而不是 UML或Basic的命令。
        
        argv = util_split_command_args(str_action)
        if len(argv) == 0:
            logging.debug('One empty line: %s.' % str_action)
            return
        
        if argv[0] == "quit":
            pkg = CommandPackage(CommandId.QUIT_PROCESSOR)
        elif argv[0] == 'help':
            pkg = CommandPackage(CommandId.HELP_PROCESSOR)
        elif argv[0] == 'processor':
            if len(argv) != 2:
                logging.error("Processor needs a name.")
                return
            pkg = CommandPackage(CommandId.LOAD_PROCESSOR)
            pkg.processor_name = argv[1]
        elif argv[0] == 'script':
            if len(argv) != 2:
                logging.error("Script needs a file path.")
                return
        
            if not os.path.exists(argv[1]):
                logging.error("This Script path \"%s\" doesn't exist." % argv[1])
                return
            
            pkg = CommandPackage(CommandId.EXECUTE_SCRIPT)
            pkg.script_path = argv[1]
        else:
            logging.error("Unknown parser command:%s" % str_action)
            return
        
        if pkg:
            cmdPkgs.append(pkg)

        return