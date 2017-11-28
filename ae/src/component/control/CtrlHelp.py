# -*- coding:utf-8 -*-
'''
和帮助相关的UI。
'''
from gi.repository import Gtk

from framework.FwComponent import FwComponent

class CtrlHelp(FwComponent):
    def __init__(self):
        super(CtrlHelp, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = {'name':'ctrl.help.about', 'help':'show about information.'}
        manager.register_service(info, self)

        return True

    # override component
    def onSetup(self, manager):
        params = {'menu_name':'HelpMenu',
                  'menu_item_name':'HelpAbout',
                  'title':"About",
                  'accel':"<Alt>H",
                  'stock_id':Gtk.STOCK_INFO,
                  'service_name':'dialog.info'}
        manager.request_service("view.menu.add", params)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.help.about":
            manager.request_service('dialog.info')
            return (True, None)

        else:
            return (False, None)