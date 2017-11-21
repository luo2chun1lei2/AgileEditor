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
from component.model.ModelProject import ModelProject

class CtrlWorkshop(FwComponent):
    def __init__(self):
        super(CtrlWorkshop, self).__init__()
        
    def onRegistered(self, manager):
        info = [{'name':'ctrl.workshop.preference', 'help':'set preference of workshop.'},
                {'name':'ctrl.workshop.new_project', 'help':'create a new project.'},
                {'name':'ctrl.workshop.open_project', 'help':'open one project.'},
                {'name':'ctrl.workshop.close_project', 'help':'close the current project.'},
                {'name':'ctrl.workshop.app_quit', 'help':'quit from app.'}
                ]
        manager.registerService(info, self)
        
    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.workshop.preference":
            self._set_workshop_preferences()
            return (True, None)
        
        elif serviceName == "ctrl.workshop.new_project":
            self._new_project()
            return (True, None)
        
        elif serviceName == "ctrl.workshop.open_project":
            prj = None
            if params is not None and 'project' in params:
                prj = params['project']
            if prj is not None and isinstance(prj, ModelProject):
                self._open_prj(prj)
            else: 
                self._open_project()
            return (True, None)
        
        elif serviceName == "ctrl.workshop.close_project":
            self._close_project()
            return (True, None)
        
        elif serviceName == "ctrl.workshop.app_quit":
            self._app_quit()
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
        
        params = {'menu_name':'ProjectMenu',
                  'menu_item_name':'ProjectNew',
                  'title':'New Project',
                  'accel':"",
                  'stock_id':Gtk.STOCK_NEW,
                  'service_name':'ctrl.workshop.new_project'}
        manager.requestService("view.menu.add", params)
        
        params = {'menu_name':'ProjectMenu',
                  'menu_item_name':'ProjectOpen',
                  'title':'Open Project',
                  'accel':"",
                  'stock_id':Gtk.STOCK_OPEN,
                  'service_name':'ctrl.workshop.open_project'}
        manager.requestService("view.menu.add", params)
        
        params = {'menu_name':'ProjectMenu',
                  'menu_item_name':'ProjectClose',
                  'title':'Close Project',
                  'accel':"",
                  'stock_id':Gtk.STOCK_CLOSE,
                  'service_name':'ctrl.workshop.close_project'}
        manager.requestService("view.menu.add", params)
        
        params = {'menu_name':'ProjectMenu',
                  'menu_item_name':'AppQuit',
                  'title':'App Quit',
                  'accel':"",
                  'stock_id':Gtk.STOCK_QUIT,
                  'service_name':'ctrl.workshop.app_quit',
                  'in_toobar':True}
        manager.requestService("view.menu.add", params)
        
        return True
    
    def _set_workshop_preferences(self):
        # 配置当前的项目
        # 设定保存在workshop的数据模型之中。
        
        workshop = FwManager.requestOneSth('workshop', 'view.main.get_current_workshop')
        
        setting = {'style': workshop.setting[ModelWorkshop.OPT_NAME_STYLE],
                   'font': workshop.setting[ModelWorkshop.OPT_NAME_FONT] }
        isOK, results = FwManager.instance().requestService('dialog.project.setting',
                        {'parent':None, 'setting':setting})
        setting = results['setting']
        if setting is None:
            return

        # 修改系统设定！
        FwManager.instance().requestService('view.multi_editors.change_editor_style', {'style': setting['style']})
        FwManager.instance().requestService('view.multi_editors.change_editor_font', {'font': setting['font']})

        workshop.setting[ModelWorkshop.OPT_NAME_STYLE] = setting['style']
        workshop.setting[ModelWorkshop.OPT_NAME_FONT] = setting['font']

        workshop.save_conf()
    
    def _new_project(self):
        ''' 新建项目 '''

        isOK, results = FwManager.instance().requestService("dialog.project.new", {'parent':None})
        prj_name = results['prj_name']
        prj_src_dirs = results['prj_src_dirs']

        if prj_name is None:
            return False

        workshop = FwManager.requestOneSth('workshop', 'view.main.get_current_workshop')
        prj = workshop.create_project(prj_name, prj_src_dirs)
        if prj is None:
            logging.error("Failed to create project:%s, and src dirs:%s", (prj_name, prj_src_dirs))
            return False

        # 预处理
        prj.prepare()

        FwManager.instance().requestService('view.main.set_current_project', {'project':prj})

        workshop.add_project(prj)

        return True
    
    def _open_project(self, prj_name=None):
        ''' 打开项目 '''

        prj = None
        
        workshop = FwManager.requestOneSth('workshop', 'view.main.get_current_workshop')
        if prj_name:
            for each_prj in workshop.projects:
                if each_prj.prj_name == prj_name:
                    prj = each_prj
        else:
            isOK, results = FwManager.instance().requestService("dialog.project.open",
                                        {'parent':None, 'workshop':workshop})
            prj = results['project']

        if prj is None:
            return False

        return self._open_prj(prj)
    
    def _open_prj(self, prj):
        # 使用这个Project，并开始进行初始化。
        prj.prepare()

        FwManager.instance().requestService('view.main.set_current_project', {'project':prj})

        # 打开代码所在的目录
        # TODO:有多个代码的项目，应该显示哪个目录？
        if len(prj.src_dirs) > 0:
            FwManager.instance().requestService('view.fstree.set_dir', {'dir':prj.src_dirs[0]})

        # 设置窗口标题。
        FwManager.instance().requestService('view.main.set_title', {'title':''})

        # 设置终端属性。
        FwManager.instance().requestService('view.terminal.init', {'dir':prj.src_dirs[0]})
        return True
    
    def _close_project(self):
        ''' 关闭当前的项目 '''
        FwManager.instance().requestService('view.main.close_current_project')
        
    def _app_quit(self):
        ''' 如果打开了当前文件，且修改过了，需要保存。
            关闭当前文件。退出程序。
        '''
        isOK, results = FwManager.instance().requestService('view.main.close_files')
        result = results['result']
        if result != ViewWindow.RLT_OK:
            return result

        Gtk.main_quit()