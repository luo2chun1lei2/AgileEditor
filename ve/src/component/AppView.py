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
            self._show(params)
            return (True, None)
        else:
            return (False, None)

    def _show(self, setting):
        # 进入主管理组件，传入需要的参数。
        from VeMain import VeMain
        veMain = VeMain.get_instance()
        veMain.start(setting['want_lazy'], setting['want_open_project_name'], setting['want_open_file'])
