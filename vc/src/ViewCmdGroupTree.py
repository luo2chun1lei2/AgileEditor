#-*- coding:utf-8 -*-

'''
显示命令组的列表（不用树的结构）
'''

import os
import stat
import time
import collections
from collections import OrderedDict

from gi.repository import GObject, Gtk, Gdk, GtkSource, GLib, GdkPixbuf
from bzrlib.tree import Tree
from ViewMenu import *
from VcCmd import VcCmdGroup

class CmdGroupGObject(GObject.GObject):
    
    __gtype_name__ = 'CmdGroupGObject'
    
    def __init__(self, cmdgroup):

        GObject.GObject.__init__(self)
        self.cmdgroup = cmdgroup
                 
# 需要注册这个对象到GObject中。
GObject.type_register(CmdGroupGObject)

# TODO:目前这个不是一个控件，希望以后变成一个控件。
class ViewCmdGroupTree:
    ''' 
    命令组的列表
    外部是滚动条，内部是ListView。
    '''
    (COLUMN_NAME,
     COLUMN_IS_OK,
     COLUMN_START_PROCESS,
     COLUMN_PROGRESS,
     COLUMN_CMD_OBJ,
     NUM_COLUMNS) = range(6)

    def __init__(self, on_menu_func, vc_cmd_groups):

        self.on_menu_func = on_menu_func
        
        # 生成模型
        self.vc_cmd_groups = vc_cmd_groups
        self.treeview = Gtk.TreeView()
        self.show_cmd_grps(vc_cmd_groups)
        
        self.treeview.set_rules_hint(True)
        
        self.add_columns(self.treeview)
        self.treeview.connect("row-activated", self.on_row_activated)

        scrolledWindow = Gtk.ScrolledWindow()
        scrolledWindow.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolledWindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledWindow.add(self.treeview)
        
        self.scrolledWindow = scrolledWindow
    
    def show_cmd_grps(self, cmd_groups):
        self.model = self._create_model(self.vc_cmd_groups)

        # 创建TreeView的控件
        self.treeview.set_model(self.model)
        
    def _create_model(self, cmd_groups):
        model = Gtk.ListStore( str,                 # 命令的名字
                               bool, # 是否在运行，以及运行结果
                               bool,
                               GObject.TYPE_INT,     # 进度条
                               GObject.TYPE_OBJECT
                               )

        col = 0
        self.data = cmd_groups
        for cmdgroup in self.data:
            
            process = cmdgroup.get_process()
            # 根据命令当前的进度得到运行的情况。
            if process == 0:
                # 还没有运行
                icon_name = ""
                start_process = False
                
            elif process < 100:
                # 正在运行
                icon_name = ""
                start_process = True
                
            elif process == 100:
                # 运行完成（成功）
                icon_name = Gtk.STOCK_OK
                start_process = False
                process = 0
                
            else: # < 0
                # 运行失败
                icon_name = Gtk.STOCK_NO
                start_process = False
                process = 0
                
            model.append([cmdgroup.key, icon_name, start_process, process, CmdGroupGObject(cmdgroup)])
            col += 1
        return model

    def add_columns(self, treeview):
        
        model = treeview.get_model()

        # 命令名字
        renderer = Gtk.CellRendererText()
        renderer.connect("edited", self.on_cmdgroup_name_changed);
        self.renderer_name = renderer
        self.renderer_name.set_property("editable", True)
        
        column = Gtk.TreeViewColumn("命令组", renderer, text=self.COLUMN_NAME)
        #column.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        column.set_alignment(0.5)
        column.set_expand(True)
        column.set_resizable(True)
        
        treeview.append_column(column)

        # 是否成功
        renderer = Gtk.CellRendererPixbuf()
        renderer.props.follow_state = True
        
        column = Gtk.TreeViewColumn("结果", renderer, stock_id = self.COLUMN_IS_OK)
                                    #sensitive=self.COLUMN_SENSITIVE)
        #column.set_sort_column_id(self.COLUMN_ICON)
        column.set_min_width(50)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        
        column.set_expand(False)
        column.set_alignment(0.5)
        
        treeview.append_column(column)
        
        # 是否正在运行
        renderer = Gtk.CellRendererSpinner()
        
        column = Gtk.TreeViewColumn("运行", renderer, pulse=self.COLUMN_PROGRESS,
                                    active=self.COLUMN_START_PROCESS)
        column.set_min_width(50)
        column.set_sizing(Gtk.TreeViewColumnSizing.FIXED)
        column.set_alignment(0.5)
        
        treeview.append_column(column)
        
    def on_cmdgroup_name_changed(self, cell, path_str, new_text):
        # 修改命令组的名字
        model = self.model
        iter_ = model.get_iter(path_str)
        vc_cmdgroup = model.get_value(iter_, self.COLUMN_CMD_OBJ).cmdgroup
        
        vc_cmdgroup.set_key(new_text)
        
        model.set_value(iter_, self.COLUMN_NAME, vc_cmdgroup.get_key())
        
    def on_row_activated(self, treeview, path_str, column):
        # 点击其中一个行
        model = self.model
        iter_ = model.get_iter(path_str)
        vc_cmdgroup = model.get_value(iter_, self.COLUMN_CMD_OBJ).cmdgroup
        
        self.on_menu_func(None, ViewMenu.ACTION_COMMAND_GROUP_OPEN, vc_cmdgroup)
        
    def add_new_cmd_grp(self, cmd_grp_name):
        self.vc_cmd_groups.append( VcCmdGroup(cmd_grp_name) )
        
        # TODO:也可以不用这么重新生成model，可以通过listStore的添加功能完成。
        self.show_cmd_grps(self.vc_cmd_groups)
        