# -*- coding:utf-8 -*-

'''
负责检索和跳转用的。
'''
from gi.repository import Gtk

from framework.FwComponent import FwComponent
from component.util.UtilEditor import UtilEditor

class CtrlSearch(FwComponent):
    def __init__(self):
        super(CtrlSearch, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.search.jump_to', 'help':'Jump to ? line.'},
                {'name':'ctrl.search.select_all', 'help':'select all test in current edit file.'}
                ]
        manager.registerService(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.search.jump_to":
            self._jump_to_line()
            return (True, None)
        elif serviceName == 'ctrl.search.uncomment':
            self._edit_uncomment()
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

    def _jump_to_line(self):
        from component.util.UtilDialog import UtilDialog

        # 显示一个对话框，输入需要跳转的行。
        response, text = UtilDialog.show_dialog_one_entry("跳转到行", '行')
        if response != Gtk.ResponseType.OK or text is None or text == '':
            return

        if text.isdigit():
            line_number = int(text)
        else:
            line_number = -1

        if line_number != -1:
            UtilEditor.jump_to(line_number)
