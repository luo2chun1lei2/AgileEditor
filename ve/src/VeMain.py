#!/usr/bin/env python
#-*- coding:utf-8 -*-

#######################################
## VE主入口程序，并且管理窗口和数据。

import os, sys, getopt, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango
from gi.overrides.Gtk import TextBuffer

from ModelWorkshop import ModelWorkshop
from ModelProject import ModelProject
from ViewDialogTags import ViewDialogTagsOpen
from ModelFile import ModelFile
from ViewMenu import ViewMenu
from ViewFsTree import ViewFsTree, FsTreeModel
from ViewTagList import ViewTagList
from ViewHelp import ViewDialogInfo
from ViewMultiEditors import ViewMultiEditors
from ViewWindow import ViewWindow

from VeEventPipe import VeEventPipe

class VeMain():
    # 数据是 workshop -> project + file，
    # 而画面就可能有各种情况了。
    # ve_path string ve配置的路径

    DEFAULT_VE_CONFIG_PATH = '~/.ve'
    
    ve_main_instance = None
    
    @staticmethod
    def get_instance():
        if VeMain.ve_main_instance is None:
            VeMain.ve_main_instance = VeMain()
            
        return VeMain.ve_main_instance

    def __init__(self):
        
        # 加载数据模型
        self.ve_path = os.path.expanduser(VeMain.DEFAULT_VE_CONFIG_PATH)
        self.workshop = ModelWorkshop(self.ve_path)
        
        # 在EventPipe注册事件处理方法。
        VeEventPipe.register_event_call_back(VeEventPipe.EVENT_WANT_ADD_NEW_PROJECT, self.add_new_project)
        VeEventPipe.register_event_call_back(VeEventPipe.EVENT_WANT_DEL_PROJECT, self.del_project)
        VeEventPipe.register_event_call_back(VeEventPipe.EVENT_WANT_CHANGE_PROJECT, self.change_project)

    def start(self, want_open_project_name, want_open_file):
        # 开始启动程序。
        
        from ViewDialogProject import ViewDialogProjectNew, ViewDialogProjectOpen
        
        # 打开想要打开的项目
        prj = None
        if not want_open_project_name is None:
            prj = self.workshop.get_prj(want_open_project_name)
        
        # 如果没有传入打开某个项目，或者指定的项目不存在，那么就指定一个。
        if prj is None :
            # 需要让客户选择一个项目
            prj = ViewDialogProjectOpen.show(None, self.workshop)
            
        if prj is None:
            # 客户还是选择失败，或者退出，那么就不用再运行了。
            print "指定的项目不存在。"
            return
        
        # 创建窗口，注册关闭事件
        editorWin = ViewWindow(self.workshop, prj, want_open_file)
        editorWin.connect("delete-event", Gtk.main_quit)
        
        # - 全屏
        editorWin.maximize()
        
        # - 设定图标。
        base_path = os.path.dirname((os.path.abspath(sys.argv[0])))
        editorWin.set_icon_from_file(os.path.join(base_path, "ve.png"))
        
        # - 显示画面
        editorWin.show_all()
        
        # - 并进入主循环。
        Gtk.main()
        
    def add_new_project(self, prj_name, prj_src_dirs):
        
        prj_path = os.path.join(self.workshop.ws_path, prj_name)
        prj = ModelProject.create(prj_path, prj_name, prj_src_dirs)
        
        # 预处理
        prj.prepare()

        self.workshop.add_project(prj)
        
    def del_project(self, prj):
        prj.remove()
        self.workshop.del_project(prj)
        
    def change_project(self, prj, prj_name, prj_src_dirs):
        # 将指定的项目变成新的名字和代码路径。
        
        # - 删除旧的项目
        self.del_project(prj)
        
        # - 加入新的项目
        self.add_new_project(prj_name, prj_src_dirs)

        