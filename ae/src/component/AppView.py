# -*- coding:utf-8 -*-
'''
应用程序的画面。
主画面并不一定是Window，为了适应以后的扩展，需要有一个显示方面的总体组件。
'''

import logging

from framework.FwComponent import FwComponent

class AppView(FwComponent):
    def __init__(self):
        super(AppView, self).__init__()

    def onRegistered(self, manager):
        info = {'name':'app.view.show', 'help':'show the main view of application.'}
        manager.register_service(info, self)
        return True

    def onRequested(self, manager, serviceName, params):
        if serviceName == "app.view.show":
            logging.debug("show main view and into loop")
            manager.request_service('app.select_project',
                    {'want_lazy':params['want_lazy'],
                     'want_open_project_name':params['want_open_project_name'],
                     'want_open_file':params['want_open_file']})
            return (True, None)
        else:
            return (False, None)
