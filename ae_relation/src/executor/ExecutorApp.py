# -*- coding:utf-8 -*-

# Executor:
# 执行的目标是App。


import os, sys, logging

from executor.Executor import *
from parser.CommandPackage import *

class ExecutorApp(Executor):
    # 执行的目标是application.
    
    def __init__(self, app):
        super(ExecutorApp, self).__init__()
        self.app = app
        
    def execute(self, cmdPkg):
        # @param cmdPkg CommandPackage，需要执行的命令
        
        if cmdPkg.cmdId == CommandId.SET_LOG_LEVEL:
            # set log and level.
            logging.basicConfig(level=cmdPkg.level,
                format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

        elif cmdPkg.cmdId == CommandId.SHOW_APP_HELP:
            self.app.show_help()
            
        elif cmdPkg.cmdId == CommandId.QUIT:
            if cmdPkg.error:
                sys.exit(1)
            else:
                sys.exit(0)

        elif cmdPkg.cmdId == CommandId.LOAD_PROCESSOR:
            if not self.app.init_processor(cmdPkg.processor_name):
                sys.exit(1)
        
        elif cmdPkg.cmdId == CommandId.LOAD_DATA:
            if not self.app.load_model_data(cmdPkg.data_name):
                sys.exit(1)

        elif cmdPkg.cmdId == CommandId.EXECUTE_SCRIPT:
            if not self.app.execute_script(cmdPkg.script_path):
                sys.exit(1)

        elif cmdPkg.cmdId == CommandId.ENTER_INTERVIEW:
            # if it's interview mode, run for a loop until return quit.
            self.app.enter_interview()
        
        