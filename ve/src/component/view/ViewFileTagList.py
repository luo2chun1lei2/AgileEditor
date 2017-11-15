# -*- coding:utf-8 -*-

# 在List中显示Tags。
# TODO 使用ctags工具的时候，应该用Tree来表示类和函数之间的包含关系。

import logging
from gi.repository import Gtk, Gdk, GObject, GLib

from component.model.ModelTags import ModelTag
from framework.FwUtils import *
from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ViewFileTagList (FwComponent):
    # 定制一个ListView，内部显示Tag。
    # editorWindow:EditorWindow:总的编辑窗口。

    # 设定一个栏目的枚举常量。
    (
     COLUMN_TAG_TYPE,  # 类型
     COLUMN_TAG_NAME,  # Tag名字
     COLUMN_TAG_LINE_NO,  # 行号
     COLUMN_TAG_SCOPE,  # 所在范围
     ) = range(4)

    def __init__(self):
        # editorWindow:ViewWindow:主画面

        # 总的容器
        vbox = Gtk.VBox(spacing=2)

        # 显示标题
        label = Gtk.Label(label='Tag List')
        # isOK, color = Gdk.Color.parse("White")
        # label.modify_bg(Gtk.StateType.NORMAL, color)
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

    # override component
    def onRegistered(self, manager):
        info = [{'name':'view.file_taglist.get_view', 'help':'get view of tag list.'},
                {'name':'view.file_taglist.show_taglist', 'help':'show tag list in view.'}]
        manager.registerService(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.file_taglist.get_view":
            return (True, {'view':self.get_view()})

        elif serviceName == "view.file_taglist.show_taglist":
            self.set_model(params['taglist'])
            self.expand_all()
            return (True, None)

        else:
            return (False, None)

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

        model = Gtk.TreeStore(str, str, GObject.TYPE_INT, str)

        # 加入的逻辑：
        # 如果碰到tag有scope的，就放入到上面和scope同名的class中。
        last_tag = None
        last_itr = None
        for tag in tags:
            if is_empty(tag.tag_scope):
                # 如果没有范围，就放在顶层
                last_itr = self._add_tag_with_group(model, last_tag, last_itr, tag)
            else:
                if last_tag is None:
                    # 如果是第一个，就形成自己的组
                    last_itr = self._add_tag_with_group(model, last_tag, last_itr, tag)
                else:
                    # 如果有上一个
                    if tag.tag_scope == last_tag.tag_scope:
                        # 和上一个相等，就放在一个组中
                        last_itr = model.insert_after(None, last_itr,
                                [tag.tag_type, tag.tag_name, tag.tag_line_no, tag.tag_scope])
                    elif tag.tag_scope == last_tag.tag_name:
                        last_itr = model.insert_after(last_itr, None,
                                [tag.tag_type, tag.tag_name, tag.tag_line_no, tag.tag_scope])
                    else:
                        # 和上一个不同，则建立自己的组和自己
                        last_itr = self._add_tag_with_group(model, last_tag, last_itr, tag)
            last_tag = tag
        return model

    def _add_tag_with_group(self, model, last_tag, last_itr, tag):
        # 根据scope找到对应的tag，如果没有找到就返回None
        # scope:string:tag的scope名字
        # return:TreeIter:找到的Iter
        if is_empty(tag.tag_scope):
            last_itr = model.append(None,
                        [tag.tag_type, tag.tag_name, tag.tag_line_no, tag.tag_scope])
        else:
            itr = model.append(None, ["scope", tag.tag_scope, -1, ""])  # 组
            last_itr = model.append(itr,
                        [tag.tag_type, tag.tag_name, tag.tag_line_no, tag.tag_scope])

        return last_itr

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
        column.set_alignment(0.5)  # 标题的对齐
        treeview.append_column(column)

        # column for tag
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("名字", renderer, text=self.COLUMN_TAG_NAME)
        column.set_sort_column_id(self.COLUMN_TAG_NAME)
        column.set_alignment(0.5)  # 标题的对齐
        treeview.append_column(column)

#         # column for tag
#         renderer = Gtk.CellRendererText()
#         column = Gtk.TreeViewColumn("Scope", renderer, text=self.COLUMN_TAG_SCOPE)
#         column.set_sort_column_id(self.COLUMN_TAG_SCOPE)
#         column.set_alignment(0.5) # 标题的对齐
#         treeview.append_column(column)

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
        line_no = model.get_value(miter, self.COLUMN_TAG_LINE_NO)

        logging.debug('tag line no=%d' % line_no)

        if line_no < 0:
            # 不应该跳转的项目
            return

        # 跳转到对应的行。
        FwManager.instance().requestService('view.main.goto_line', {'line_no':line_no})

    def get_view(self):
        # 返回容器控件
        # return:Widget:自身需要加入到容器中的控件。

        return self.view

    def expand_all(self):
        self.taglistview.expand_all()
