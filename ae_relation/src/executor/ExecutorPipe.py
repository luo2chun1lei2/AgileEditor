# -*- coding:utf-8 -*-

# Executor:
# 执行的目标是Pipe。

import logging

from executor.Executor import *

# TODO:这里的pipe是app, ExecutorPipe名字并不对。因为它不是针对Pipe的执行！
class ExecutorPipe(Executor):
    # 针对Pipe执行命令。

    def __init__(self, pipe):
        super(ExecutorPipe, self).__init__()
        self.pipe = pipe

    def execute(self, cmdPkg):
        logging.debug("Execute pipe command:%s" % cmdPkg.cmdId)

        # TODO 命令解析用 getopt，这样就允许用参数了。
        if cmdPkg.commandId == CommandId.HELP_PIPE:
            self.pipe.show_inner_command_help()
        elif cmdPkg.commandId == CommandId.QUIT_PIPE:
            self.pipe.quit()
        else:
            print "Unknown parser command:%s" % str_action
            
        return Return.OK

