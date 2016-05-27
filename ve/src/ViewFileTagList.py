#-*- coding:utf-8 -*-

# 在List中显示Tags。
# TODO 使用ctags工具的时候，应该用Tree来表示类和函数之间的包含关系。

import logging
from gi.repository import Gtk, Gdk, GObject, GLib
from ModelTags import ModelTag

class ViewFileTagList:
    # 定制一个ListView，内部显示Tag。
    # ideWindow:EditorWindow:总的编辑窗口。
    
    # 设定一个栏目的枚举常量。
    (
     COLUMN_TAG_TYPE, # 类型
     COLUMN_TAG_NAME,  # Tag名字
     COLUMN_TAG_LINE_NO, # 行号
     COLUMN_TAG_SCOPE, # 所在范围
     ) = range(4)

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
        
        # 生成数据模型(空的)
        self.model = self._create_model([])
        
        treeview = Gtk.TreeView(model=self.model)
        
        # 添加每列的Render
        self._add_columns(treeview)
        
        treeview.set_rules_hint(True)
        treeview.set_search_column(self.COLUMN_TAG_NAME)
        treeview.connect("row-activated", self._on_row_activated)
        
        sw.add(treeview)
        
        vbox.pack_start(sw, True, True, 0)

        # 设定需要传出的控件。
        self.view = vbox
        self.taglistview = treeview
        
    def set_model(self, tags):
        # 设置模型
        # tags:[string]:tag信息的数组
        # return:Nothing
        
        self.model = self._create_model(tags)
        self.taglistview.set_model(self.model)
        
    def _create_model(self, tags):
        # 根据Tag生成对应的Model。
        # tags:[string]:tag的信息列表
        # return:TreeModel:生成TreeModel数据
        
        model = Gtk.ListStore(str, str, GObject.TYPE_INT, str)

        for tag in tags:
            model.append([tag.tag_type, tag.tag_name, tag.tag_line_no, tag.tag_scope])
        
        return model
        
    def _add_columns(self, treeview):
        # 给TreeView添加栏的Render
        # treeview:TreeView:
        # return:Nothing

        # column for type
        renderer = Gtk.CellRendererText()
        # 颜色参考 /usr/share/X11/rgb.txt 文件。
        renderer.set_property("cell-background", "light grey");
        column = Gtk.TreeViewColumn("类型", renderer, text=self.COLUMN_TAG_TYPE)
        column.set_sort_column_id(self.COLUMN_TAG_TYPE)
        column.set_alignment(0.5) # 标题的对齐
        treeview.append_column(column)

        # column for tag
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("名字", renderer, text=self.COLUMN_TAG_NAME)
        column.set_sort_column_id(self.COLUMN_TAG_NAME)
        column.set_alignment(0.5) # 标题的对齐
        treeview.append_column(column)
        
        # column for tag
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Scope", renderer, text=self.COLUMN_TAG_SCOPE)
        column.set_sort_column_id(self.COLUMN_TAG_SCOPE)
        column.set_alignment(0.5) # 标题的对齐
        treeview.append_column(column)
        
        # column for line no
#         renderer = Gtk.CellRendererText()
#         # 颜色参考 /usr/share/X11/rgb.txt 文件。
#         renderer.set_property("cell-background", "grey");
#         column = Gtk.TreeViewColumn("行号", renderer, text=self.COLUMN_TAG_LINE_NO)
#         column.set_sort_column_id(self.COLUMN_TAG_LINE_NO)
#         column.set_alignment(0.5) # 标题的对齐
#         treeview.append_column(column)
        
    def _on_row_activated(self, treeview, path, column):
        # 当双击了Tag时
        
        # 得到行号
        model = treeview.get_model()
        miter = model.get_iter(path)
        line_no = model.get_value(miter, 2)
        
        logging.debug('tag line no=%d' % line_no)
        # 跳转到对应的行。
        self.ideWindow.ide_goto_line(line_no)
        
        # 编辑器获取焦点。
        self.ideWindow.ide_editor_set_focus()
        
    def get_view(self):
        # 返回容器控件
        # return:Widget:
        
        return self.view
