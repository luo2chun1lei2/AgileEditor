# -*- coding:utf-8 -*-

# 应用程序层：
# 建立基本的 “parser、executor、model” pipe。

from __future__ import unicode_literals

import os, sys, logging, getopt, shutil, traceback
from parser.Control import *
from mvc.model.TestModel1 import *

from pipe.Pipe import *
from parser.Parser import *
from app.ParserCommandArgument import *
from executor.Executor import *

# 用于命令提示

reload(sys)
sys.setdefaultencoding('utf8')

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

class AppExecutor(Executor):
    # 执行
    
    def __init__(self, app):
        super(AppExecutor, self).__init__()
        self.app = app
        
    def execute(self, cmdPkg):
        # @param cmdPkg CommandPackage，需要执行的命令
        
        if cmdPkg.cmdId == CommandId.SET_LOG_LEVEL:
            # set log and level.
            logging.basicConfig(level=cmdPkg.level,
                format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

        elif cmdPkg.cmdId == CommandId.SHOW_HELP:   #TODO 这里不正确，help和exit在一起。
            self.app.parserCommandArgument.show_help()
            if cmdPkg.error:
                sys.exit(1)
            else:
                sys.exit(0)

        elif cmdPkg.cmdId == CommandId.EXECUTE_SCRIPT:
            # if set script file, execute it.
            self.app._execute_script(cmdPkg.script_path)

        elif cmdPkg.cmdId == CommandId.ENTER_INTERVIEW: #TODO: 必须放在所有命令的后面，否则退出有问题。
            # if it's interview mode, run for a loop until return quit.
            self.app._enter_interview()
        
        elif cmdPkg.cmdId == CommandId.MODEL_NAME:  # TODO 有先后顺序，必须在执行脚本前执行。
            # TODO: Container是哪里来的？
            container = TestContainer(cmdPkg.model_name)
            self.app.parser = Parser(container)
            
class App():

    def __init__(self):
        self.parser = None
        self.executor = AppExecutor(self)
        self.parserCommandArgument = ParserCommandArgument()
    
    def do(self, argv):
        cmdPkgs = self.parserCommandArgument.parse(argv)
        for cmdPkg in cmdPkgs:
            self.executor.execute(cmdPkg)

    def _execute_script(self, script_path):
        # 执行一个脚本文件。
        # script_path : string: path of script file
        # return : bool: True, OK, False, failed.
        try:
            logging.debug('Open script "%s", and execute it.' % script_path)
            f = open(script_path)
            
            # 读取文件中的每一行处理，如果行末有“\"，那么就将此行之下合并为此行。
            cmd = ""
            line_no = 0
            for l in f:
                line_no += 1
                ll = l.replace('\n', '').strip()
                if len(ll) > 0 and ll[-1] == '\\':
                    cmd += ll[:-1]
                    continue
                else:
                    cmd += ll
                    
                logging.debug('Execute line[%d]: %s' % (line_no, cmd))
                rtn = self.parser.do(cmd)
                if rtn != Return.OK:
                    break
                
                cmd = ""
                    
        except Exception, ex:
            print ex.message
            traceback.print_exc()
            return False
        return True

    # 在内部控制或者脚本可以执行的命令。
    # TODO : 应该用当前Parser或者当前Control来提供
    CMDLINE_CMD = ['help', 'quit', 'test',
                    'select', 'from', 'insert', 'update', 'delete', 'drop']

    def _enter_interview(self):
        
        # 设定命令的提示符号。
        # TODO 提示的关键字，需要和下面的命令解析配套。
        word_completer = WordCompleter(App.CMDLINE_CMD, ignore_case=True)
        
        while True:
            input_str = prompt('>', completer=word_completer,
                  complete_while_typing=False)

            rtn = self.parser.do(input_str)
            if rtn == Return.QUIT:
                break
            
            
