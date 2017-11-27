# -*- coding:utf-8 -*-

#######################################
# # VE主入口程序，并且管理窗口和数据。

import os, sys, logging
from gi.repository import Gtk

from framework.FwManager import FwManager
from component.model.ModelWorkshop import ModelWorkshop
from component.view.ViewWindow import ViewWindow
from framework.FwComponent import FwComponent

class AeMain(FwComponent):
    # 数据是 workshop -> project + file，
    # 而画面就可能有各种情况了。
    # ve_path string ve配置的路径

    def __init__(self):

        # 加载数据模型
        self.ve_path = os.path.expanduser(ModelWorkshop.DEFAULT_VE_CONFIG_PATH)
        self.workshop = ModelWorkshop(self.ve_path)

    def onRegistered(self, manager):
        manager.load('model_workshop', self.workshop)

        info = {'name':'app.select_project', 'help':'select one project to start UI.'}
        manager.registerService(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "app.select_project":
            self._start(params['want_lazy'],
                        params['want_open_project_name'],
                        params['want_open_file'])
            return True, None
        else:
            return (False, None)

    def _find_corresponding_project(self):
        # 根据当前路径，找到合适的项目。
        # return:string:项目的名字，没有找到，None
        cwd = os.getcwd()
        return self.workshop.find_project_by_src_path(cwd)

    def _start(self, want_lazy, want_open_project_name, want_open_file):
        # 开始启动程序，主要要选择打开哪个project。

        # 打开想要打开的项目
        prj = None
        if want_open_project_name is None and want_lazy:
            want_open_project_name = self._find_corresponding_project()

        if not want_open_project_name is None:
            prj = self.workshop.get_project(want_open_project_name)

        # 如果没有传入打开某个项目，或者指定的项目不存在，那么就指定一个。
        if prj is None :
            # 需要让客户选择一个项目
            isOK, results = FwManager.instance().requestService("dialog.project.open",
                                        {'parent':None, 'workshop':self.workshop})
            if not isOK:
                return
            prj = results['project']

        if prj is None:
            # 客户还是选择失败，或者退出，那么就不用再运行了。
            return

        # 创建窗口，注册关闭事件
        editorWin = ViewWindow(self.workshop, prj, want_open_file)

        editorWin.connect("delete-event", Gtk.main_quit)

        # - 全屏
        # TODO 无法记住之前的位置和大小吗？
        editorWin.maximize()

        # - 设定图标。
        base_path = os.path.dirname((os.path.abspath(sys.argv[0])))
        editorWin.set_icon_from_file(os.path.join(base_path, "ae.png"))

        FwManager.instance().load('view_main', editorWin)
        # TODO 现在服务之间相互调用，已经出现先后顺序的问题，因为有的组件生成实例时，
        #      就需要调用服务。
        FwManager.instance().requestService('ctrl.workshop.open_project', {'project':prj})

        # - 显示画面
        editorWin.show_all()

        # - 并进入主循环。
        Gtk.main()
