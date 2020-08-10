# -*- coding:utf-8 -*-

# 针对Model的Executor。

import logging, getopt

from model import *
from model.concrete.ModelBasic import *
from misc.Return import *
from misc.Utils import *
from parser.CommandPackage import *


class ExecutorModelBasic(object):
    # 执行针对ModelBasic的command package。
    
    def __init__(self, model, output):
        super(ExecutorModelBasic, self).__init__()
        self.model = model
        self.output = output
        self.no = 0
        
    def execute(self, cmdPkg):
        
        if cmdPkg.cmdId == CommandId.SHOW_HELP:
            self.show_help()
        elif cmdPkg.cmdId == CommandId.MODEL_SHOW:
            # 为了显示，就需要 Model和Output配合。
            self.output.show(self.model, cmdPkg)

        elif cmdPkg.cmdId == CommandId.MODEL_ELEMENT:
            # 元素
            self.model.create_element(cmdPkg)
            
        elif cmdPkg.cmdId == CommandId.MODEL_RELATION:
            # 关系。
            self.model.create_relation(cmdPkg)
        
        else:
            return Return.UNKNOWN

        return Return.OK

    def show_help(self):
        print 'command:'
        print 'help: show help information.'
        print 'element: add element.'
        print 'relation: add relation.'
