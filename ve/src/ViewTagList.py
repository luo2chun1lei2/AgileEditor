#-*- coding:utf-8 -*-

# 在List中显示Tags。
# 显示信息不够完成，还缺少idutils工具支持。

import logging
from gi.repository import Gtk, Gdk, GObject, GLib
from ModelTags import ModelTag

class ViewTagList:
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

        # 总的容器
        vbox = Gtk.VBox(spacing=2)
        
        # 显示标题
        label = Gtk.Label(label='Tag List')
        #isOK, color = Gdk.Color.parse("White")
        #label.modify_bg(Gtk.StateType.NORMAL, color)
        vbox.pack_start(label, False, False, 0)

        # Tag列表包含在一个ScrollWindow中。
        sw = Gtk.ScrolledWindow()
        sw.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        self.model = self.create_model([])
        
        treeview = Gtk.TreeView(model=self.model)
        treeview.set_rules_hint(True)
        treeview.set_search_column(self.COLUMN_TAG_NAME)
        treeview.connect("row-activated", self.on_row_activated)
        sw.add(treeview)

        self.add_columns(treeview)
        vbox.pack_start(sw, True, True, 0)

        # 设定需要传出的控件。
        self.view = vbox
        self.taglistview = treeview
        
    def create_model(self, tags):
        # 根据Tag生成对应的Model。
        model = Gtk.ListStore(GObject.TYPE_INT, str)

        for tag in tags:
            model.append([tag.tag_line_no, tag.tag_name])
        
        return model
        
    def set_model(self, tags):
        # 设置模型
        self.model = self.create_model(tags) 
        self.taglistview.set_model(self.model)

    def add_columns(self, treeview):
        model = treeview.get_model()

        # column for line no
        renderer = Gtk.CellRendererText()
        # 颜色参考 /usr/share/X11/rgb.txt 文件。
        renderer.set_property("cell-background", "light grey");
        column = Gtk.TreeViewColumn("行号", renderer,
                                    text=self.COLUMN_TAG_LINE_NO)
        column.set_sort_column_id(self.COLUMN_TAG_LINE_NO)
        treeview.append_column(column)

        # column for tag
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("名字", renderer,
                                    text=self.COLUMN_TAG_NAME)
        column.set_sort_column_id(self.COLUMN_TAG_NAME)
        treeview.append_column(column)
        
    def on_row_activated(self, treeview, path, column):
        # 当双击了Tag时
        
        # 得到行号
        model = treeview.get_model()
        miter = model.get_iter(path)
        line_no = model.get_value(miter, 0)
        
        logging.debug('tag line no=%d' % line_no)
        # 跳转到对应的行。
        self.ideWindow.ide_goto_line(line_no)
        
        # 编辑器获取焦点。
        self.ideWindow.ide_editor_set_focus()
        
