# -*- coding:utf-8 -*-
'''
应用程序的主画面。
'''

import logging

from framework.FwComponent import FwComponent

class AppView(FwComponent):
    def __init__(self):
        pass

    def onRegistered(self, manager):
        info = {'name':'app.view', 'help':'show the main view of application.'}
        manager.registerService(info, self)
        return True

    def onRequested(self, manager, serviceName, params):
        if serviceName == "app.view":
            logging.debug("show main view and into loop")
            manager.requestService('app.select_project',
                    {'want_lazy':params['want_lazy'],
                     'want_open_project_name':params['want_open_project_name'],
                     'want_open_file':params['want_open_file']})
            return (True, None)
        else:
            return (False, None)
