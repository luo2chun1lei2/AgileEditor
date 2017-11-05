# -*- coding:utf-8 -*-
'''
分析输入的命令。
'''
import logging
from framework.FwBaseComponent import FwBaseComponent

class CommandParser:
    def __init__(self):
        pass
    
    def init(self, manager):
        info = {'name':'command.parse', 'help':'parse the command options, and return result.'}
        manager.registerService(info, self)
        return True

    def dispatchService(self, manager, serviceName, params):
        if serviceName == "command.parse":
            logging.debug("parse command")
            
            return (True, None)
        else:
            return (False, None)