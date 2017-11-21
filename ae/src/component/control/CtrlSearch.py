# -*- coding:utf-8 -*-

'''
负责检索和跳转用的。
'''
from framework.FwComponent import FwComponent

class CtrlSearch(FwComponent):
    def __init__(self):
        super(CtrlSearch, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.edit.redo', 'help':'redo.'},
                {'name':'ctrl.edit.select_all', 'help':'select all test in current edit file.'}
                ]
        manager.registerService(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.edit.comment":
            self._edit_comment()
            return (True, None)
        elif serviceName == 'ctrl.edit.uncomment':
            self._edit_uncomment()
            return (True, None)
        else:
            return (False, None)

    # override component
    def onSetup(self, manager):

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditReplace',
                  'title':"Replace",
                  'accel':"<control>R",
                  'stock_id':None,
                  'service_name':'ctrl.edit.replace'}
        manager.requestService("view.menu.add", params)

        return True
