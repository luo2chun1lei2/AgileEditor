#-*- coding:utf-8 -*-

###########################################################
# 关于项目的对话框
# 以“项目列表对话框”为核心，新建、修改都是从此出发，当然这两个对话框也可以单独调用。

import os, string
import ConfigParser

from gi.repository import Gtk, Gdk

from VeUtils import *
from ModelProject import ModelProject
from VeEventPipe import VeEventPipe

###########################################################

class ViewDialogProjectNew(Gtk.Dialog):
    # 新建项目的对话框
    # 有可能需要有多个路径，比如用于排斥，或者用于和其他项目进行引用。
    
    def __init__(self, parent):
        
        self.parent = parent
        
        Gtk.Dialog.__init__(self, "新建项目 ", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
        self.set_default_size(300, 400)
        
        vbox = Gtk.VBox(spacing = 10)
        
        ###############################
        ## 项目名字
        lbl_prj_name = Gtk.Label("项目名字")
        lbl_prj_name.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(lbl_prj_name, False, True, 0)
        
        self.entry_prj_name = Gtk.Entry()
        vbox.pack_start(self.entry_prj_name, True, True, 0)
         
        ###############################
        ## 代码位置
        ## TODO: 无法允许有多个路径，但是是否可以实验去掉若干路径？还有查询辅助库。
        lbl_src_path = Gtk.Label("代码路径")
        vbox.pack_start(lbl_src_path, True, True, 0)
                
        self.picker_src_path = Gtk.FileChooserButton.new('请选择一个文件夹 ', 
                                                         Gtk.FileChooserAction.SELECT_FOLDER)
        vbox.pack_start(self.picker_src_path, True, True, 1.0)
         
        ###############################
        box = self.get_content_area()
        box.add(vbox)
        
        self.show_all()
    
    @staticmethod
    def show(parent):
        dialog = ViewDialogProjectNew(parent)
        
        prj_name = None
        prj_src_path = None
        
        while True:
        
            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                # 如果选择OK的话，就创建对应的Project项目。
                prj_name = dialog.entry_prj_name.get_text()
                prj_src_path = dialog.picker_src_path.get_filename()
                
                if is_empty(prj_name):
                    # 项目名字为空，重新回到对话框
                    continue
                    
                if is_empty(prj_src_path):
                    # 项目文件路径为空，重新回到对话框
                    continue
                
            break
        
        dialog.destroy()
        
        # 返回信息。
        return prj_name, [prj_src_path]
    
###########################################################

class ViewDialogProjectChange(Gtk.Dialog):
    # 修改Project的对话框
    
    def __init__(self, parent):
        
        self.parent = parent
        
        Gtk.Dialog.__init__(self, "修改项目 ", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
        self.set_default_size(300, 400)
        
        vbox = Gtk.VBox(spacing = 10)
        
        ###############################
        ## 项目名字
        lbl_prj_name = Gtk.Label("项目名字")
        lbl_prj_name.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(lbl_prj_name, False, True, 0)
        
        self.entry_prj_name = Gtk.Entry()
        vbox.pack_start(self.entry_prj_name, True, True, 0)
         
        ###############################
        ## 代码位置（TODO:应该允许有多个）
        lbl_src_path = Gtk.Label("代码路径")
        vbox.pack_start(lbl_src_path, True, True, 0)
                
        self.picker_src_path = Gtk.FileChooserButton.new('请选择一个文件夹 ', 
                                                         Gtk.FileChooserAction.SELECT_FOLDER)
        vbox.pack_start(self.picker_src_path, True, True, 1.0)
         
        ###############################
        box = self.get_content_area()
        box.add(vbox)
        
        self.show_all()
    
    @staticmethod
    def show(parent, prj):
        
        dialog = ViewDialogProjectNew(parent)
        
        prj_name = None
        prj_src_path = None
        
        dialog.entry_prj_name.set_text(prj.prj_name)
        dialog.picker_src_path.set_current_folder(prj.src_dirs[0])
        
        need_show = True
        while need_show:
        
            response = dialog.run()
            
            if response == Gtk.ResponseType.OK:
                # 如果选择OK的话，就创建对应的Project项目。
                prj_name = dialog.entry_prj_name.get_text()
                prj_src_path = dialog.picker_src_path.get_filename()
                if is_empty(prj_name):
                    # 重新回到对话框
                    continue
                    
                if is_empty(prj_src_path):
                    # 重新回到对话框
                    continue
                
            need_show = False
        
        dialog.destroy()
        
        # 返回信息。
        return prj_name, [prj_src_path]
    
###########################################################

class ViewDialogProjectOpen(Gtk.Dialog):
    # 显示Project的列表的对话框
    # prj_treeview:ModelProject:被选中的项目。
    # ideWorkshop:ModelWorkshop:
    
    REPONSE_TYPE_NEW_PRJ = 100
    REPONSE_TYPE_DEL_PRJ = 101
    REPONSE_TYPE_CHANGE_PRJ = 102
    
    def __init__(self, parent, ideWorkshop):
    
        self.parent = parent
        self.ideWorkshop = ideWorkshop
        self.selected_project = None
        
        Gtk.Dialog.__init__(self, "打开项目", parent, 0,
                            (Gtk.STOCK_NEW, ViewDialogProjectOpen.REPONSE_TYPE_NEW_PRJ, # 新项目
                             Gtk.STOCK_DELETE, ViewDialogProjectOpen.REPONSE_TYPE_DEL_PRJ, # 删除项目
                             Gtk.STOCK_EDIT, ViewDialogProjectOpen.REPONSE_TYPE_CHANGE_PRJ, # 改变项目
                             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, # 退出
                             Gtk.STOCK_OK, Gtk.ResponseType.OK # 打开项目
                             ))
        
        self.set_default_size(600, 400)
        
        vbox = Gtk.VBox(spacing = 10)
        
        ###############################
        ## 项目名字
        lbl_prj_list = Gtk.Label("项目列表")
        lbl_prj_list.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(lbl_prj_list, False, True, 0)
        
        ###############################
        ## 项目的列表(项目的名字|项目的路径)。
    
        treeview = Gtk.TreeView()
        treeview.connect("row-activated", self.on_row_activated)
        
        renderer_prj_name = Gtk.CellRendererText()
        #renderer_prj_name.connect("row-activated", self.on_render_selected)
        column_prj_name = Gtk.TreeViewColumn("项目名字", renderer_prj_name, text=0)
        
        treeview.append_column(column_prj_name)
        
        renderer_prj_dir = Gtk.CellRendererText()
        column_prj_dir = Gtk.TreeViewColumn("路径", renderer_prj_dir, text=1)
        treeview.append_column(column_prj_dir)
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(300, 300)
        scrolledwindow.add(treeview)
        
        vbox.pack_start(scrolledwindow, True, True, 0)
         
        ###############################
        box = self.get_content_area()
        box.pack_start(vbox, True, True, 0)
        
        self.prj_treeview = treeview
        
        # 显示数据
        self._show_data()
        
        self.show_all()
        
    def _show_data(self):
        ideWorkshop = self.ideWorkshop
        liststore = Gtk.ListStore(str, str)
        
        for prj in ideWorkshop.projects:
            # TODO 似乎代码路径只能有一个，虽然写的是数组。
            #liststore.append([prj.prj_name, os.path.dirname(prj.src_dirs[0])])
            liststore.append([prj.prj_name, prj.src_dirs[0]])
            
        self.prj_treeview.set_model(liststore)
        
    def on_render_selected(self, widget, path, column):
        self.selected_project = self.ideWorkshop[path]
    
    @staticmethod
    def show(parent, ideWorkshop):
        # 显示画面，然后返回是被选中的项目。
        # 如果一个都没有选，就返回None
        
        dialog = ViewDialogProjectOpen(parent, ideWorkshop)
        
        while True:
        
            prj = None
            response = dialog.run()
                
            if response == Gtk.ResponseType.OK:
                # 如果选择OK的话，就创建对应的Project项目。
                selection = dialog.prj_treeview.get_selection()
                
                if selection.get_selected():
                    selected_pathes = selection.get_selected_rows()[1]
                    if len(selected_pathes) == 0:
                        continue
                    
                    selected_index = selected_pathes[0].get_indices()[0]
                    prj = dialog.ideWorkshop.projects[selected_index]
                
                break
                    
            elif response == ViewDialogProjectOpen.REPONSE_TYPE_NEW_PRJ:
                # 创建一个新的对话框
                prj_name, prj_src_dirs = ViewDialogProjectNew.show(dialog)
                if not prj_name is None:
                    # 发动“添加一个新的项目”的动作。
                    VeEventPipe.want_add_new_project(prj_name, prj_src_dirs)
                    
                # 更新当前画面。
                dialog._show_data()
                    
            elif response == ViewDialogProjectOpen.REPONSE_TYPE_DEL_PRJ:
                # 删除一个项目 
                selection = dialog.prj_treeview.get_selection()
                
                if selection.get_selected():
                    selected_pathes = selection.get_selected_rows()[1]
                    if len(selected_pathes) == 0:
                        continue
                    
                    selected_index = selected_pathes[0].get_indices()[0]
                    prj = dialog.ideWorkshop.projects[selected_index]
                    
                    VeEventPipe.want_del_project(prj)
                    
                # 更新当前画面。
                dialog._show_data()
                    
            elif response == ViewDialogProjectOpen.REPONSE_TYPE_CHANGE_PRJ:
                # 修改一个项目 
                selection = dialog.prj_treeview.get_selection()
                
                if selection.get_selected():
                    selected_pathes = selection.get_selected_rows()[1]
                    if len(selected_pathes) == 0:
                        continue
                    
                    selected_index = selected_pathes[0].get_indices()[0]
                    prj = dialog.ideWorkshop.projects[selected_index]
                    
                    prj_name, prj_src_dirs = ViewDialogProjectChange.show(dialog, prj)
                    if not prj_name is None:
                        VeEventPipe.want_change_project(prj, prj_name, prj_src_dirs)
                    
                # 更新当前画面。
                dialog._show_data()
                    
            else:
                # 其他情况，就直接退出。
                break
        
        # 关闭对话框
        dialog.destroy()
        
        # 返回信息。
        return prj
    
    def on_row_activated(self, treeview, path_str, column):
        # 双击，如同点了OK按钮。
        self.response(Gtk.ResponseType.OK)
