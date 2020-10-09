# -*- coding:utf-8 -*-

# Executor:
# 执行的目标是Processor。

import logging

from executor.Executor import *
from parser.CommandPackage import *
from misc.Return import *

class ExecutorProcessor(Executor):
    # 针对Processor执行命令。

    def __init__(self, processor):
        super(ExecutorProcessor, self).__init__()
        self.processor = processor

    def execute(self, cmdPkg):
        # @param cmdPkg CommandPackage
        logging.debug("Execute processor command:%s" % cmdPkg.cmdId)

        if cmdPkg.cmdId == CommandId.HELP_PROCESSOR:
            self.processor.show_help()
        elif cmdPkg.cmdId == CommandId.QUIT_PROCESSOR:
            self.processor.quit()
        else:
            #logging.error("Unknown parser command:%s" % cmdPkg.cmdId)
            return Return.UNKNOWN
            
        return Return.OK

