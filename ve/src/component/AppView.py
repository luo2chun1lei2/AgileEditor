# -*- coding:utf-8 -*-
'''
应用程序的主画面。
'''

import logging

from framework.FwBaseComponent import FwBaseComponent
from VeMain import VeMain

class AppView(FwBaseComponent):
    def __init__(self):
        pass

    def init(self, manager):
        info = {'name':'app.view', 'help':'show the main view of application.'}
        manager.registerService(info, self)
        return True

    def dispatchService(self, manager, serviceName, params):
        if serviceName == "app.view":
            logging.debug("show main view and into loop")
            self._show(params)
            return (True, None)
        else:
            return (False, None)

    def _show(self, setting):
        # 进入主管理组件，传入需要的参数。
        veMain = VeMain.get_instance()
        veMain.start(setting['want_lazy'], setting['want_open_project_name'], setting['want_open_file'])