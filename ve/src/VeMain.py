# -*- coding:utf-8 -*-

#######################################
# # VE主入口程序，并且管理窗口和数据。

import os, sys, getopt, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango

from framework.FwManager import FwManager

from component.model.ModelWorkshop import ModelWorkshop
from component.model.ModelProject import ModelProject
from component.model.ModelFile import ModelFile

from component.view.ViewWindow import ViewWindow
from framework.FwComponent import FwComponent

class VeMain(FwComponent):
    # 数据是 workshop -> project + file，
    # 而画面就可能有各种情况了。
    # ve_path string ve配置的路径

    DEFAULT_VE_CONFIG_PATH = '~/.ve'

    ve_main_instance = None
    # 静态单实例

    @staticmethod
    def get_instance():
        if VeMain.ve_main_instance is None:
            VeMain.ve_main_instance = VeMain()
            FwManager.instance().load("vemain", VeMain.ve_main_instance)

        return VeMain.ve_main_instance

    def __init__(self):

        # 加载数据模型
        self.ve_path = os.path.expanduser(VeMain.DEFAULT_VE_CONFIG_PATH)
        self.workshop = ModelWorkshop(self.ve_path)

        FwManager.instance().load('model_workshop', self.workshop)

    def onRegistered(self, manager):
        info = {'name':'project.new', 'help':'create a new project in model.'}
        manager.registerService(info, self)

        info = {'name':'project.delete', 'help':'delete the given project in model.'}
        manager.registerService(info, self)

        info = {'name':'project.change', 'help':'change the given project in model.'}
        manager.registerService(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "project.new":
            self.add_new_project(params['project_name'], params['source_pathes'])
            return (True, None)

        elif serviceName == "project.delete":
            self.del_project(params['project'])
            return (True, None)

        elif serviceName == "project.change":
            self.change_project(params['project'], params['project_name'], params['source_pathes'])
            return (True, None)

        else:
            return (False, None)

    def find_corresponding_project(self):
        # 根据当前路径，找到合适的项目。
        # return:string:项目的名字，没有找到，None
        cwd = os.getcwd()
        return self.workshop.find_project_by_src_path(cwd)

    def start(self, want_lazy, want_open_project_name, want_open_file):
        # 开始启动程序。

        # 打开想要打开的项目
        prj = None
        if want_open_project_name is None and want_lazy:
            want_open_project_name = self.find_corresponding_project()

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
        editorWin.set_icon_from_file(os.path.join(base_path, "ve.png"))

        # - 显示画面
        editorWin.show_all()

        FwManager.instance().load('view_main', editorWin)

        # - 并进入主循环。
        Gtk.main()

    def add_new_project(self, prj_name, prj_src_dirs):
        ''' 添加一个新的项目
        @param prj_name: string: project name
        @param prj_src_dirs: [string]: source path of project.
        '''
        prj = self.workshop.create_project(prj_name, prj_src_dirs)

        if prj is None:
            return

        # 预处理
        prj.prepare()

        self.workshop.add_project(prj)

    def del_project(self, prj):
        ''' 删除一个项目
        @param prj: ModelProject
        '''
        prj.remove()
        self.workshop.del_project(prj)

    def change_project(self, prj, prj_name, prj_src_dirs):
        ''' 将指定的项目变成新的名字和代码路径。
        @param prj: ModelProject: old project
        @param prj_name: string: project name
        @param prj_src_dirs: [string]: source path of project.
        '''

        # - 删除旧的项目
        self.del_project(prj)

        # - 加入新的项目
        self.add_new_project(prj_name, prj_src_dirs)
