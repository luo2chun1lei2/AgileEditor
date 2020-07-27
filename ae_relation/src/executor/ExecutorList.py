# -*- coding:utf-8 -*-

# 执行多个命令。

import logging

from misc import *
from parser import *

class ExecutorList(object):
    # 按照初始化时，传入的Executor的顺序执行。
    # 如果一个executor返回执行成功，那么就跳出。
    # 如果一个executor返回“未知”，那么就继续执行。
    
    def __init__(self, *executors):
        super(ExecutorList, self).__init__()
        self.executors = executors
        

    def execute(self, cmdPkg):
        rlt = Return.UNKNOWN
        for e in self.executors:
            rlt = e.execute(cmdPkg)
            if rlt != Return.UNKNOWN:
                break
        
        # TODO: 这里还是问题，如果允许组合，那么哪一层是最外层可以显示错误信息？
        if rlt == Return.UNKNOWN:
            logging.error ("Unknown command:%d" % cmdPkg.cmdId)
        
        return rlt
            