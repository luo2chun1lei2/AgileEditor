# -*- coding:utf-8 -*-

''' 显示书签列表。
'''

import logging
from gi.repository import Gtk, Gdk, GObject, GLib

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ViewBookmarks(FwComponent):
    ''' 显示一个List，可以加入标签，并且激活标签。
    editorWindow:EditorWindow:总的编辑窗口。
    '''

    # 设定一个栏目的枚举常量。
    (
     COLUMN_TAG_LINE_NO,  # 行号
     COLUMN_TAG_NAME,  # Tag名字
     NUM_COLUMNS) = range(3)

    def __init__(self):
        self.cur_prj = None

        self._init_view()

    # override component
    def onSetup(self, manager):
        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchAddBookmark',
                  'title':"Add bookmark",
                  'accel':"<control>B",
                  'stock_id':Gtk.STOCK_GO_BACK,
                  'service_name': 'view.bookmarks.add_bookmark'}
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchRemoveBookmark',
                  'title':"Remove bookmark",
                  'accel':"<shift><control>B",
                  'stock_id':Gtk.STOCK_GO_BACK,
                  'service_name': 'view.bookmarks.remove_bookmark'}
        manager.requestService("view.menu.add", params)

        return True

    # override component
    def onRegistered(self, manager):
        info = [{'name':'view.bookmarks.add_bookmark', 'help':'add one bookmark by current pos.'},
                {'name':'view.bookmarks.remove_bookmark', 'help':'remove one bookmark by current pos.'},
                {'name':'view.bookmarks.get_view', 'help':'get view of bookmark.'}]
        manager.registerService(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == 'view.bookmarks.get_view':
            return (True, {'view': self.get_view()})
        
        elif serviceName == "view.bookmarks.add_bookmark":
            # 获取根据当前情况而建立的bookmark。
            isOK, results = manager.requestService("ctrl.search.make_bookmark")
            if not isOK:
                return (False, None)

            # 更新显示。'
            self.cur_prj = results['current_project']
            self.set_model(results['bookmarks'], self.cur_prj)

            return (True, None)

        elif serviceName == "view.bookmarks.remove_bookmark":
            # 删除一条书签。
            selected_index = self.get_selected()
            if selected_index < 0:
                return (True, None)

            if self.cur_prj is None:
                return (False, None)

            self.cur_prj.remove_bookmark(selected_index)

            self.set_model(self.cur_prj.bookmarks, self.cur_prj)
            return (True, None)

        else:
            return (False, None)

    def _init_view(self):
        ''' 初始化画面 '''
        vbox = Gtk.VBox(spacing=0)

        ###############################
        # # 项目名字
        # lbl_tag_list = Gtk.Label("Tag列表")
        # lbl_tag_list.set_justify(Gtk.Justification.LEFT)
        # vbox.pack_start(lbl_tag_list, False, True, 0)

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
        scrolledwindow.set_size_request(0, 100)  # 有作用
        scrolledwindow.add(treeview)

        vbox.pack_start(scrolledwindow, True, True, 0)

        # 设定需要传出的控件。
        self.view = vbox
        self.taglistview = treeview

    def set_model(self, tags, prj):
        # 设置数据
        # tags:[ModelTag]:tag信息的数组
        # prj:ModelProject:当前的项目信息
        # return:Nothing

        self.tags = tags

        ###############################
        # 项目的列表(项目的名字|项目的路径)。
        liststore = Gtk.ListStore(str, str, str)

        for tag in tags:
            # 去掉路径前缀
            file_path = tag.tag_file_path
            if prj is not None:
                file_path = file_path.replace(prj.src_dirs[0] + '/', '')
            liststore.append([file_path, str(tag.tag_line_no), tag.tag_content])

        self.taglistview.set_model(liststore)

    def _on_row_activated(self, treeview, path, column):
        # 当双击了Tag时，引起激活tag事件。

        selection = treeview.get_selection()

        if selection.get_selected():
            selected_pathes = selection.get_selected_rows()[1]
            selected_index = selected_pathes[0].get_indices()[0]
            tag = self.tags[selected_index]

            # 跳转到对应的行。
            FwManager.instance().requestService('ctrl.search.show_bookmark', {'tag':tag})

    def get_view(self):
        # 返回容器控件
        # return: Widget: 显示控件，可以放到任意容器中。

        return self.view

    def get_selected(self):
        # 找到当前选中的项目
        # return: int: 选中的索引，-1，没有选中。
        selection = self.taglistview.get_selection()

        itr = selection.get_selected()[1]
        if itr:
            selected_pathes = selection.get_selected_rows()[1]
            return selected_pathes[0].get_indices()[0]
        else:
            return -1
