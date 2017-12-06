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
        ''' 目前此组件没有自己的service，因为加入的菜单可以直接调用对应的service，不需要此组件协调。
        '''
        return True

    # override component
    def onSetup(self, manager):
        params = {'menu_name':'HelpMenu',
                  'menu_item_name':'HelpAbout',
                  'title':"About",
                  'accel':"<Alt>H",
                  'stock_id':Gtk.STOCK_ABOUT,
                  'service_name':'dialog.about'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'HelpMenu',
                  'menu_item_name':'HelpInfo',
                  'title':"Information",
                  'accel':"<Alt>I",
                  'stock_id':Gtk.STOCK_INFO,
                  'service_name':'dialog.info'}
        manager.request_service("view.menu.add", params)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
            return (False, None)
