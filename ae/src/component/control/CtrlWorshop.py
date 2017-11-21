# -*- coding:utf-8 -*-

'''
Workshop的控制类
'''

import logging
from gi.repository import Gdk, GLib, Gtk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

from component.model.ModelTask import ModelTask
from component.model.ModelWorkshop import ModelWorkshop
from component.util.UtilEditor import UtilEditor
from component.util.UtilDialog import UtilDialog
from component.view.ViewWindow import ViewWindow

class CtrlWorkshop(FwComponent):
    def __init__(self):
        super(CtrlWorkshop, self).__init__()
        
    def onRegistered(self, manager):
        info = [{'name':'ctrl.workshop.preference', 'help':'set preference of workshop.'},
                {'name':'ctrl.workshop.go_back_tag', 'help':'go back to the previous tag.'}
                ]
        manager.registerService(info, self)
        
    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.workshop.preference":
            self._set_workshop_preferences()
            return (True, None)
        
        else:
            return (False, None)

    # override component
    def onSetup(self, manager):
        params = {'menu_name':'ProjectMenu',
                  'menu_item_name':'WorkshopPreferences',
                  'title':'Preferences',
                  'accel':"",
                  'stock_id':Gtk.STOCK_PREFERENCES,
                  'service_name':'ctrl.workshop.preference'}
        manager.requestService("view.menu.add", params)
        
        return True
    
    def _set_workshop_preferences(self):
        # 配置当前的项目
        # 设定保存在workshop的数据模型之中。
        
        workshop = FwManager.requestOneSth('workshop', 'view.main.get_current_workshop')
        
        setting = {'style': workshop.setting[ModelWorkshop.OPT_NAME_STYLE],
                   'font': workshop.setting[ModelWorkshop.OPT_NAME_FONT] }
        isOK, results = FwManager.instance().requestService('dialog.project.setting',
                        {'parent':self, 'setting':setting})
        setting = results['setting']
        if setting is None:
            return

        # 修改系统设定！
        FwManager.instance().requestService('view.multi_editors.change_editor_style', {'style': setting['style']})
        FwManager.instance().requestService('view.multi_editors.change_editor_font', {'font': setting['font']})

        self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_STYLE] = setting['style']
        self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_FONT] = setting['font']

        workshop.save_conf()