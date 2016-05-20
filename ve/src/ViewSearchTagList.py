#-*- coding:utf-8 -*-

# 显示检索后的Tag列表
# 比如，文件名字检索、项目内名字检索、定义或者引用之类的。

import logging
from gi.repository import Gtk, Gdk, GObject, GLib
from ModelTags import ModelTag

class ViewSearchTagList:
    # 定制一个ListView，内部显示Tag。
    # ideWindow:EditorWindow:总的编辑窗口。
    
    # 设定一个栏目的枚举常量。
    (
     COLUMN_TAG_LINE_NO, # 行号
     COLUMN_TAG_NAME,  # Tag名字
     NUM_COLUMNS) = range(3)

    def __init__(self, ideWindow):
        # ideWindow:ViewWindow:主画面

        self.ideWindow = ideWindow

        vbox = Gtk.VBox(spacing = 0)
        
        ###############################
        ## 项目名字
        #lbl_tag_list = Gtk.Label("Tag列表")
        #lbl_tag_list.set_justify(Gtk.Justification.LEFT)
        #vbox.pack_start(lbl_tag_list, False, True, 0)
         
        # TreeView
        treeview = Gtk.TreeView()
        
        renderer_file_path = Gtk.CellRendererText()
        column_prj_name = Gtk.TreeViewColumn("路径", renderer_file_path, text=0)
        treeview.append_column(column_prj_name)
        
        renderer_line_number = Gtk.CellRendererText()
        renderer_line_number.set_property("cell-background", "light grey")
        column_prj_dir = Gtk.TreeViewColumn("行号", renderer_line_number, text=1)
        treeview.append_column(column_prj_dir)
        
        renderer_content = Gtk.CellRendererText()
        column_content = Gtk.TreeViewColumn("内容", renderer_content, text=2)
        treeview.append_column(column_content)
        
        treeview.connect("row-activated", self._on_row_activated)
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(0, 100) # 有作用
        scrolledwindow.add(treeview)
        
        vbox.pack_start(scrolledwindow, True, True, 0)
        
        # 设定需要传出的控件。
        self.view = vbox
        self.taglistview = treeview
        
    def set_model(self, tags, prj):
        # 设置模型
        # tags:[string]:tag信息的数组
        # prj:ModelProject:当前的项目信息
        # return:Nothing
        
        self.tags = tags
        
        ###############################
        ## 项目的列表(项目的名字|项目的路径)。
        liststore = Gtk.ListStore(str, str, str)
        
        for tag in tags:
            # 去掉路径前缀
            file_path = tag.tag_file_path
            if prj is not None:
                file_path = file_path.replace(prj.src_dirs[0] + '/', '')
            liststore.append([file_path, str(tag.tag_line_no), tag.tag_content])
            
        self.taglistview.set_model(liststore)
        
    def _on_row_activated(self, treeview, path, column):
        # 当双击了Tag时
        
        selection = treeview.get_selection()
        
        if selection.get_selected():
            selected_pathes = selection.get_selected_rows()[1]
            selected_index = selected_pathes[0].get_indices()[0]
            tag = self.tags[selected_index]
        
            # 跳转到对应的行。
            self.ideWindow.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)
            self.ideWindow.ide_editor_set_focus()
        
    def get_view(self):
        # 返回容器控件
        # return:Widget:
        
        return self.view
