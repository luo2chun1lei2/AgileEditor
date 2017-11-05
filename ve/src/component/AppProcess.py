# -*- coding:utf-8 -*-
'''
应用程序组件。
'''
import logging
from framework.FwBaseComponent import FwBaseComponent

class AppProcess(FwBaseComponent):
    def __init__(self):
        pass
    
    def init(self, manager):
        info = {'name':'app.run', 'help':'run as main application.'}
        manager.registerService(info, self)
        return True

    def dispatchService(self, manager, serviceName, params):
        if serviceName == "app.run":
            logging.debug("run application")
            
            # 命令分析
            (isOK, results) = manager.requestService("command.parse", params['argv'])
            if not isOK:
                return (False, None)
            
            # 启动主画面。
            (isOK, results) = manager.requestService("app.view", results)
            if not isOK:
                return (False, None)
            
            return (True, None)
        else:
            return (False, None)