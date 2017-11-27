# -*- coding:utf-8 -*-
'''
应用程序的主画面。
'''

import logging

from framework.FwComponent import FwComponent

class AppView(FwComponent):
    def __init__(self):
        super(AppView, self).__init__()

    def onRegistered(self, manager):
        info = {'name':'app.view', 'help':'show the main view of application.'}
        manager.register_service(info, self)
        return True

    def onRequested(self, manager, serviceName, params):
        if serviceName == "app.view":
            logging.debug("show main view and into loop")
            manager.request_service('app.select_project',
                    {'want_lazy':params['want_lazy'],
                     'want_open_project_name':params['want_open_project_name'],
                     'want_open_file':params['want_open_file']})
            return (True, None)
        else:
            return (False, None)
