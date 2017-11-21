# -*- coding:utf-8 -*-

'''
Workshop的控制类
'''

import logging
from gi.repository import Gdk, GLib, Gtk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

from component.model.ModelTask import ModelTask
from component.util.UtilEditor import UtilEditor
from component.util.UtilDialog import UtilDialog
from component.view.ViewWindow import ViewWindow

class CtrlWorkshop(FwComponent):
    def __init__(self):
        super(CtrlWorkshop, self).__init__()
        
    def onRegistered(self, manager):
        info = [{'name':'ctrl.search.init', 'help':'initialize the search context.'},
                {'name':'ctrl.search.go_back_tag', 'help':'go back to the previous tag.'}
                ]
        manager.registerService(info, self)
        
    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.search.jump_to":
            self._jump_to_line()
            return (True, None)
        
        else:
            return (False, None)

    # override component
    def onSetup(self, manager):

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchJumpTo',
                  'title':None,
                  'accel':"<control>L",
                  'stock_id':Gtk.STOCK_JUMP_TO,
                  'service_name':'ctrl.search.jump_to'}
        manager.requestService("view.menu.add", params)
        
        return True