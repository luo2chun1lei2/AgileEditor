#-*- coding:utf-8 -*-

'''
和Tag相关的对话框。
'''

import os
import ConfigParser
from gi.repository import GObject, Gtk, Gdk, GtkSource

from VeUtils import *
from ModelTags import ModelGTags
from VeWordProvider import VeWordProvider

###########################################################

class ViewDialogTagsOpen(Gtk.Dialog):
    ''' 显示Tag的列表的对话框
    tags:[IdeOneTag]:Tag列表。
    '''
    
    def __init__(self, parent, tags):
    
        self.parent = parent
        self.tags = tags
        self.selected_project = None
        
        Gtk.Dialog.__init__(self, "选择Tag", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
        self.set_default_size(800, 600)
        self.set_default_response(Gtk.ResponseType.OK)
        
        vbox = Gtk.VBox(spacing = 10)
        
        ###############################
        ## 项目名字
        lbl_tag_list = Gtk.Label("Tag列表")
        lbl_tag_list.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(lbl_tag_list, False, True, 0)
         
        ###############################
        ## 项目的列表(项目的名字|项目的路径)。
        liststore = Gtk.ListStore(str, str, str)
        
        for tag in tags:
            liststore.append([tag.tag_file_path, str(tag.tag_line_no), tag.tag_content])
            
        treeview = Gtk.TreeView(model=liststore)
        
        renderer_file_path = Gtk.CellRendererText()
        column_prj_name = Gtk.TreeViewColumn("路径", renderer_file_path, text=0)
        treeview.append_column(column_prj_name)
        
        renderer_line_number = Gtk.CellRendererText()
        renderer_line_number.set_property("cell-background", "yellow")
        column_prj_dir = Gtk.TreeViewColumn("行号", renderer_line_number, text=1)
        treeview.append_column(column_prj_dir)
        
        renderer_content = Gtk.CellRendererText()
        column_content = Gtk.TreeViewColumn("内容", renderer_content, text=2)
        treeview.append_column(column_content)
        
        treeview.connect("row-activated", self.on_row_activated)
        
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_size_request(600, 400)
        scrolledwindow.add(treeview)
        
        vbox.pack_start(scrolledwindow, True, True, 0)
         
        ###############################
        box = self.get_content_area()
        box.add(vbox)
        
        self.prj_treeview = treeview
        
        self.show_all()
        
    def on_row_activated(self, treeview, path_str, column):
        # 双击，如同点了OK按钮。
        self.response(Gtk.ResponseType.OK)
    
    @staticmethod
    def show(parent, tags):
        ''' 返回是被选中的项目。'''
        
        dialog = ViewDialogTagsOpen(parent, tags)
        
        tag = None
        response = dialog.run()
            
        if response == Gtk.ResponseType.OK:
            # 如果选择OK的话，就创建对应的Project项目。
            selection = dialog.prj_treeview.get_selection()
            
            if selection.get_selected():
                selected_pathes = selection.get_selected_rows()[1]
                selected_index = selected_pathes[0].get_indices()[0]
                tag = dialog.tags[selected_index]
        
        dialog.destroy()
        
        # 返回信息。
        return tag
    