# -*- coding:utf-8 -*-
'''
应用程序的主画面。
'''
import logging
from framework.FwBaseComponent import FwBaseComponent

class AppView:
    def __init__(self):
        pass
    
    def init(self, manager):
        info = {'name':'app.view', 'help':'show the main view of application.'}
        manager.registerService(info, self)
        return True

    def dispatchService(self, manager, serviceName, params):
        if serviceName == "app.view":
            logging.debug("show main view and into loop")
            
            return (True, None)
        else:
            return (False, None)