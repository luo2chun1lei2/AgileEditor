# -*- coding:utf-8 -*-
'''
应用程序组件。
'''
from framework.FwBaseComponent import FwBaseComponent

class AppProcess(FwBaseComponent):
    def __init__(self):
        pass
    
    def init(self, manager):
        info = {'name':'app.run', 'help':'run as main application.'}
        manager.registerService(info, self)
        return True

    def dispatchService(self, serviceName, params):
        if serviceName == "app.run":
            
            return (True, None)
        else:
            return (False, None)