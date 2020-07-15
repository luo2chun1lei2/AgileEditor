# -*- coding:utf-8 -*-

# Executor:
# 执行的目标是App。


import os, sys, logging

from executor.Executor import *
from parser.CommandPackage import *

class ExecutorApp(Executor):
    # 执行
    
    def __init__(self, app):
        super(ExecutorApp, self).__init__()
        self.app = app
        
    def execute(self, cmdPkg):
        # @param cmdPkg CommandPackage，需要执行的命令
        
        if cmdPkg.cmdId == CommandId.SET_LOG_LEVEL:
            # set log and level.
            logging.basicConfig(level=cmdPkg.level,
                format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

        elif cmdPkg.cmdId == CommandId.SHOW_HELP:   #TODO 这里不正确，help和exit在一起。
            self.app.parserApp.show_help()
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
            self.app.init_parser_container(cmdPkg.model_name)