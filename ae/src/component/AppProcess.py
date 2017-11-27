# -*- coding:utf-8 -*-
'''
应用程序组件。
负责整个app的初始化等流程，有比较复杂的 dispatch 实现。
'''
import logging
from framework.FwComponent import FwComponent

class AppProcess(FwComponent):
    def __init__(self):
        super(AppProcess, self).__init__()

    def onRegistered(self, manager):
        info = {'name':'app.run', 'help':'run as main application.'}
        manager.register_service(info, self)
        return True

    def onRequested(self, manager, serviceName, params):
        if serviceName == "app.run":
            logging.debug("run application")

            # 命令分析
            (isOK, results) = manager.request_service("app.command.parse", {'argv':params['argv']})
            if not isOK:
                manager.request_service("command.help", None)
                return (False, None)
            logging.debug("service's results: \"%s\"" % results)

            # 启动主画面。
            (isOK, results) = manager.request_service("app.view.show", results)
            if not isOK:
                return (False, None)

            return (True, None)
        else:
            return (False, None)


