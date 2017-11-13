# -*- coding:utf-8 -*-

#######################################
# 编辑器窗口
# 1, 顶部是菜单和工具栏（内容都随着选中的对象而定）。
# 2, 项目浏览器
# 3, 编辑器，使用GtkSourceView。
# 4, 代码浏览工具。
# 5, 编译和调试工具。
# 6, 命令工具（可以编写任意的命令）

import os, sys, getopt, shutil, re, logging
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango, Vte
from gi.overrides.Gtk import TextBuffer

from framework.FwUtils import *
from framework.FwManager import FwManager

from model.ModelWorkshop import ModelWorkshop
from model.ModelProject import ModelProject
from model.ModelFile import ModelFile
from model.ModelTask import ModelTask
from model.ModelTags import *

from ViewMenu import ViewMenu
from ViewFsTree import ViewFsTree, FsTreeModel
from ViewFileTagList import ViewFileTagList
from ViewSearchTagList import ViewSearchTagList
from ViewBookmarks import ViewBookmarks
from ViewMultiEditors import ViewMultiEditors
from framework.FwComponent import FwComponent

class ViewWindow(Gtk.Window, FwComponent):

    # ideWorkshop:ModelWorkshop:当前的workshop。
    # cur_prj:ModelProject:当前打开的项目。

    ###################################
    # 返回值的定义
    RLT_OK = 0
    RLT_CANCEL = 1  # 取消
    RLT_ERROR = 2  # 错误

    # 主窗口的标题。
    PROGRAM_NAME = 'AgileEditor v2.0 - '

    # override component
    def onRegistered(self, manager):
        info = {'name':'view.main.show_bookmark', 'help':'show a bookmark.'}
        manager.registerService(info, self)

        info = {'name':'view.main.make_bookmark', 'help': 'make one bookmark by current pos, and return bookmarks list'}
        manager.registerService(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.main.show_bookmark":  # 显示一个bookmark
            tag = params['tag']  # ModelTag
            self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)
            self.ide_editor_set_focus()
            return (True, None)

        elif serviceName == "view.main.make_bookmark":
            return self._svc_add_bookmark()

        else:
            return (False, None)

    ''' 主窗口。 '''
    def __init__(self, workshop, prj, want_open_file):

        # 跳转的记录。
        self.jumps = []
        self.cur_prj = None
        self.word_pattern = re.compile("[a-zA-Z0-9_]")

        # 读取workshop的信息。

        self.ideWorkshop = workshop

        # 创建画面
        self._create_layout()

        # 初始化状态
        if prj:
            self._ide_open_prj(prj)

        if want_open_file:
            path = os.path.abspath(want_open_file)
            self.ide_open_file(None, path)

    def _create_layout(self):
        # 创建画面。

        # TODO 下面的布局太乱，应该清晰化和通用化。
        Gtk.Window.__init__(self, title=self.PROGRAM_NAME)

        # 这个不能缺少，当不是最大时，这个是第一推荐尺寸。
        self.set_default_size(1024, 768)
        ###################################################
        # # 重要控件

        # 菜单和工具栏
        self.ide_menu = ViewMenu(self, self.on_menu_func)

        # 文件系统树
        self.ideFsTree = self.create_fs_tree()

        # 多个Editor的切换Tab
        self.multiEditors = ViewMultiEditors(self.on_menu_func)
        self.tab_page = self.multiEditors.get_tab_page()

        # 文件Tag列表。
        self.ideTagList = ViewFileTagList(self)

        # 项目搜索Tag列表
        self.searchTagList = ViewSearchTagList(self)

        # 书签列表
        self.bookmarks = ViewBookmarks(self)

        # 控制台
        self.terminal = Vte.Terminal()
        # self.terminal.set_cursor_blink_mode(Vte.CursorBlinkMode.SYSTEM) # 2.90
        self.terminal.set_font(Pango.FontDescription.from_string("Ubuntu mono 12"))
        # self.terminal.set_scrollback_lines(True) 设置则没有滚动条。
        self.terminal.set_audible_bell(False)
        # self.terminal.set_input_enabled(True)    # 2.90
        self.terminal.set_scroll_on_output(True)

        scrl_terminal = Gtk.ScrolledWindow()
        scrl_terminal.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrl_terminal.set_hexpand(True)
        scrl_terminal.set_vexpand(True)
        scrl_terminal.add(self.terminal)

        # 保存项目用的各种列表的Notebook
        self.nbPrj = Gtk.Notebook()
        self.nbPrj.set_scrollable(True)

        ###################################################
        # # 布局
        # resize:子控件是否跟着paned的大小而变化。
        # shrink:子控件是否能够比它需要的大小更小。
        panedEdtiorAndTagList = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        panedEdtiorAndTagList.pack1(self.tab_page, resize=True, shrink=True)
        panedEdtiorAndTagList.pack2(self.ideTagList.get_view(), resize=False, shrink=True)

        self.nbPrj.append_page(self.searchTagList.get_view(), Gtk.Label("检索"))
        self.nbPrj.append_page(self.bookmarks.get_view(), Gtk.Label("书签"))
        self.nbPrj.append_page(scrl_terminal, Gtk.Label("控制台"))


        panedEdtiorAndSearchTag = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        panedEdtiorAndSearchTag.pack1(panedEdtiorAndTagList, resize=True, shrink=True)
        panedEdtiorAndSearchTag.pack2(self.nbPrj, resize=False, shrink=True)

        panedFsAndEditor = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        panedFsAndEditor.pack1(self.ideFsTree.get_view(), resize=False, shrink=True)
        panedFsAndEditor.pack2(panedEdtiorAndSearchTag, resize=True, shrink=True)
        panedFsAndEditor.set_position(200);

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.ide_menu.menubar, False, False, 0)
        vbox.pack_start(self.ide_menu.toolbar, False, False, 0)
        vbox.pack_start(panedFsAndEditor, True, True, 5)

        self.add(vbox)

        # 将已经生成好的控件作为组件注册到框架中。
        FwManager.instance().load("view_menu", self.ide_menu)
        FwManager.instance().load("view_bookmark", self.bookmarks)

    def create_fs_tree(self):
        # 创建文件系统树控件。
        # return:ViewFsTree:需要外部包含的控件，以及FsTree这个实例。
        fstree = ViewFsTree()

        # 加入事件。
        select = fstree.get_treeview().get_selection()
        select.connect("changed", self.on_fstree_selection_changed)

        fstree.get_treeview().connect("row-activated", self.on_fstree_row_activated)

        # 鼠标释放事件
        fstree.get_treeview().connect("button_release_event", self.on_fstree_row_button_release)

        return fstree

    ###################################
    # # 创建画面

    def create_src_list(self):
        # 显示分析结果的列表
        pass

    ###################################
    # # 回调方法
    def on_menu_func(self, widget, action, param=None, param2=None, param3=None, param4=None):
        if action == ViewMenu.ACTION_PROJECT_NEW:
            self.ide_new_project()
        elif action == ViewMenu.ACTION_PROJECT_OPEN:
            self.ide_open_project()
        elif action == ViewMenu.ACTION_PROJECT_PREFERENCES:
            self.ide_preferences_project()
        elif action == ViewMenu.ACTION_PROJECT_CLOSE:
            self.ide_close_project()
        elif action == ViewMenu.ACTION_PROJECT_UPDATE_TAGS:
            self.ide_update_tags_of_project()

        elif action == ViewMenu.ACTION_APP_QUIT:
            self.ide_quit(widget)

        elif action == ViewMenu.ACTION_FILE_NEW:
            self.ide_new_file(widget)
        elif action == ViewMenu.ACTION_FILE_OPEN:
            self.ide_open_file(widget)
        elif action == ViewMenu.ACTION_FILE_CLOSE:
            self.ide_close_file(widget)
            self.ide_new_file(widget)
        elif action == ViewMenu.ACTION_FILE_SAVE:
            self.ide_save_file(widget)
        elif action == ViewMenu.ACTION_FILE_SAVE_AS:
            self.ide_save_as_file(widget)

        # 编辑
        elif action == ViewMenu.ACTION_EDIT_REDO:
            self.ide_edit_redo(widget)
        elif action == ViewMenu.ACTION_EDIT_UNDO:
            self.ide_edit_undo(widget)
        elif action == ViewMenu.ACTION_EDIT_CUT:
            self.ide_edit_cut(widget)
        elif action == ViewMenu.ACTION_EDIT_COPY:
            self.ide_edit_copy(widget)
        elif action == ViewMenu.ACTION_EDIT_PASTE:
            self.ide_edit_paste(widget)
        elif action == ViewMenu.ACTION_EDIT_SELECT_ALL:
            self.ide_edit_select_all(widget)
        elif action == ViewMenu.ACTION_EDIT_DELETE_LINE:
            self.ide_edit_delete_line()

        elif action == ViewMenu.ACTION_EDIT_COMMENT:
            self.ide_edit_comment()
        elif action == ViewMenu.ACTION_EDIT_UNCOMMENT:
            self.ide_edit_uncomment()
        elif action == ViewMenu.ACTION_EDIT_REPLACE:
            self.ide_edit_replace()
        # 检索
        elif action == ViewMenu.ACTION_SEARCH_JUMP_TO:
            self.ide_jump_to_line(widget)
        elif action == ViewMenu.ACTION_SEARCH_FIND:
            self.ide_find(param)
        elif action == ViewMenu.ACTION_SEARCH_FIND_TEXT:
            self.ide_find_text(param, param2, param3, param4)
        elif action == ViewMenu.ACTION_SEARCH_FIND_NEXT:
            self.ide_find_next(param)
        elif action == ViewMenu.ACTION_SEARCH_FIND_IN_FILES:
            self.ide_find_in_files()
        elif action == ViewMenu.ACTION_SEARCH_FIND_PATH:
            self.ide_find_path()

        elif action == ViewMenu.ACTION_SEARCH_DIALOG_DEFINATION:
            self.ide_find_defination_by_dialog()
        elif action == ViewMenu.ACTION_SEARCH_DEFINATION:
            self.ide_search_defination()
        elif action == ViewMenu.ACTION_SEARCH_REFERENCE:
            self.ide_search_reference()
        elif action == ViewMenu.ACTION_SEARCH_BACK_TAG:
            self.ide_search_back_tag()

        elif action == ViewMenu.ACTION_EDITOR_SWITCH_PAGE:
            self.ide_switch_page(param)

        else:
            logging.error('Unknown action %d' % action)

    def on_src_bufer_changed(self, widget):
        ''' 当文件发了变化后。'''
        self._set_status(ViewMenu.STATUS_FILE_OPEN_CHANGED)

    def on_fstree_selection_changed(self, selection):
        ''' 文件列表选择时，不是双击，只是选择变化时 '''
        # model, treeiter = selection.get_selected()
        # if treeiter != None:
        #    print "You selected", model[treeiter][1]
        pass

    def on_fstree_row_activated(self, treeview, tree_path, column):
        ''' 双击了文件列表中的项目。
        如果是文件夹，就将当前文件夹变成这个文件夹。
        如果是文件，就打开。
        '''
        model = treeview.get_model()
        pathname = model._get_fp_from_tp(tree_path)
        abs_path = model.get_abs_filepath(pathname)

        if not os.access(abs_path, os.R_OK):
            logging.error('没有权限进入此目录。')
            return

        if model.is_folder(tree_path):
            # new_model = FsTreeModel(abs_path)
            # treeview.set_model(new_model)

            # self.window.set_title(new_model.dirname)

            treeview.expand_row(tree_path, False)
        else:
            # 根据绝对路径显示名字。
            self.ide_open_file(None, abs_path)

    def on_fstree_row_button_release(self, tree_view, event_button):
        # 点击了文件树的鼠标
        # tree_view:GtkTreeView:
        # event_button:EventButton:
        # return:Bool:True,已经处理了，False,没有处理。

        if event_button.type == Gdk.EventType.BUTTON_RELEASE and event_button.button == 3:
            # 右键，释放

            self.treemenu = Gtk.Menu()

            menuitem = Gtk.MenuItem.new_with_label("新建文件")
            menuitem.connect("activate", self.on_fstree_row_popup_menuitem_new_file_active, tree_view)
            self.treemenu.append(menuitem)
            menuitem.show()

            menuitem = Gtk.MenuItem.new_with_label("新建目录")
            menuitem.connect("activate", self.on_fstree_row_popup_menuitem_new_dir_active, tree_view)
            self.treemenu.append(menuitem)
            menuitem.show()

            menuitem = Gtk.MenuItem.new_with_label("删除")
            menuitem.connect("activate", self.on_fstree_row_popup_menuitem_delete_active, tree_view)
            self.treemenu.append(menuitem)
            menuitem.show()

            menuitem = Gtk.MenuItem.new_with_label("修改")
            menuitem.connect("activate", self.on_fstree_row_popup_menuitem_change_active, tree_view)
            self.treemenu.append(menuitem)
            menuitem.show()

            self.treemenu.popup(None, None, None, None, 0, event_button.time)

            return True

        else:
            return False

    def on_fstree_row_popup_menuitem_new_file_active(self, widget, tree_view):

        # 先取得选中的item
        tree_model, itr = tree_view.get_selection().get_selected()
        if itr is None:
            return

        # 得到路径
        file_path = self.ideFsTree.get_abs_file_path_by_iter(itr)

        # 如果不是目录，找到上一级的目录
        # 会不会超出项目的目录？从逻辑上看，不会。
        if not os.path.isdir(file_path):
            file_path = os.path.dirname(file_path)
            if not os.path.isdir(file_path) or not os.path.exists(file_path):
                return

        # 实现对话框，得到文件名字
        response, name = self._in_show_dialog_one_entry("新建文件", "文件名字")
        if not response == Gtk.ResponseType.OK or is_empty(name):
            return

        # 新建文件
        new_file_path = os.path.join(file_path, name)
        if os.path.exists(new_file_path):
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CLOSE, "文件“%s”已经存在。" % new_file_path)
            dialog.run()
            dialog.destroy()
            return

        f = open(new_file_path, 'w')
        f.close()

        # 刷新tree
        # self.ideFsTree.refresh_line(itr)
        self.ide_update_tags_of_project()

    def on_fstree_row_popup_menuitem_new_dir_active(self, widget, tree_view):
        # 先取得选中的item
        tree_model, itr = tree_view.get_selection().get_selected()
        if itr is None:
            return

        # 得到路径
        file_path = self.ideFsTree.get_abs_file_path_by_iter(itr)

        # 如果不是目录，找到上一级的目录
        # 会不会超出项目的目录？从逻辑上看，不会。
        if not os.path.isdir(file_path):
            file_path = os.path.dirname(file_path)
            if not os.path.isdir(file_path) or not os.path.exists(file_path):
                return

        # 实现对话框，得到文件名字
        response, name = self._in_show_dialog_one_entry("新建目录", "目录名字")
        if not response == Gtk.ResponseType.OK or is_empty(name):
            return

        # 新建文件
        new_file_path = os.path.join(file_path, name)
        if os.path.exists(new_file_path):
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CLOSE, "目录“%s”已经存在。" % new_file_path)
            dialog.run()
            dialog.destroy()
            return

        os.mkdir(new_file_path)

        # 刷新tree
        # self.ideFsTree.refresh_line(itr)
        self.ide_update_tags_of_project()

    def on_fstree_row_popup_menuitem_delete_active(self, widget, tree_view):
        # 先取得选中的item
        tree_model, itr = tree_view.get_selection().get_selected()
        if itr is None:
            return

        # 得到路径
        file_path = self.ideFsTree.get_abs_file_path_by_iter(itr)

        # 需要确认！
        dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
                                       Gtk.ButtonsType.YES_NO,
                                       "删除文件“%s”！" % file_path)
        reponse = dialog.run()
        dialog.destroy()

        if not reponse == Gtk.ResponseType.YES:
            return

        # 删除文件
        if os.path.isdir(file_path):
            shutil.rmtree(file_path)
        else:
            os.remove(file_path)

        # 刷新tree
        # self.ideFsTree.refresh_line(itr)
        self.ide_update_tags_of_project()

    def on_fstree_row_popup_menuitem_change_active(self, widget, tree_view):
        # 先取得选中的item
        tree_model, itr = tree_view.get_selection().get_selected()
        if itr is None:
            return

        # 得到路径
        file_path = self.ideFsTree.get_abs_file_path_by_iter(itr)

        # 实现对话框，得到文件名字
        response, name = self._in_show_dialog_one_entry("修改文件名字", "新文件名字")
        if not response == Gtk.ResponseType.OK or is_empty(name):
            return

        # 修改文件名字
        new_file_path = os.path.join(os.path.dirname(file_path), name)

        # 名字相等，不再替换
        if new_file_path == file_path:
            return

        if os.path.exists(new_file_path):
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,
                                       Gtk.ButtonsType.CLOSE, "文件“%s”已经存在。" % new_file_path)
            dialog.run()
            dialog.destroy()
            return

        os.rename(file_path, new_file_path)

        # 刷新tree
        # self.ideFsTree.refresh_line(itr)
        self.ide_update_tags_of_project()

    ###################################
    # # 基本功能

    def ide_new_project(self):
        # 新建项目

        isOK, results = FwManager.instance().requestService("dialog.project.new", {'parent':self})
        prj_name = results['prj_name']
        prj_src_dirs = results['prj_src_dirs']

        if prj_name is None:
            return False

        prj = self.ideWorkshop.create_project(prj_name, prj_src_dirs)
        if prj is None:
            logging.error("Failed to create project:%s, and src dirs:%s", (prj_name, prj_src_dirs))
            return False

        # 预处理
        prj.prepare()

        self.cur_prj = prj

        self.ideWorkshop.add_project(prj)

        return True

    def ide_open_project(self, prj_name=None):
        # 打开项目

        prj = None

        if prj_name:
            for each_prj in self.ideWorkshop.projects:
                if each_prj.prj_name == prj_name:
                    prj = each_prj
        else:
            isOK, results = FwManager.instance().requestService("dialog.project.open",
                                        {'parent':self, 'workshop':self.ideWorkshop})
            prj = results['project']

        if prj is None:
            return False

        return self._ide_open_prj(prj)

    def _ide_open_prj(self, prj):
        # 使用这个Project，并开始进行初始化。
        prj.prepare()

        self.cur_prj = prj

        # 打开代码所在的目录
        # TODO:有多个代码的项目，应该显示哪个目录？
        if len(prj.src_dirs) > 0:
            treeModel = FsTreeModel(prj.src_dirs[0])
            self.ideFsTree.set_model(treeModel)

        # 设置窗口标题。
        self.ide_set_title("")
        self._ide_init_ternimal()
        return True

    def ide_preferences_project(self):
        # 配置当前的项目
        # 设定保存在workshop的数据模型之中。
        setting = {'style': self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_STYLE] }
        # preferences = ViewDialogPreferences.show(self, setting)
        isOK, results = FwManager.instance().requestService('dialog.project.setting',
                        {'parent':self, 'setting':setting})
        setting = results['setting']
        if setting is None:
            return

        # 修改系统设定！
        self.multiEditors.changeEditorStyle(setting['style'])
        self.multiEditors.changeEditorFont(setting['font'])

        self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_STYLE] = setting['style']
        self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_FONT] = setting['font']

        self.ideWorkshop.save_conf()

    def ide_close_project(self):
        ''' 关闭当前的项目 '''
        self._set_status(ViewMenu.STATUS_PROJECT_NONE)

    def ide_update_tags_of_project(self):
        # 跟新当前项目的TAGS，并且更新文件列表。
        if self.cur_prj is None:
            return

        # 更新当前项目的文件列表
        treeModel = FsTreeModel(self.cur_prj.src_dirs[0])
        self.ideFsTree.set_model(treeModel)

        # 更新右边的TAGS
        self.cur_prj.prepare()

    def ide_new_file(self, widget):
        '''
        产生一个没有路径的项目文件。
        TODO:还没有决定如何实现！
        '''

        # self.multiEditors.show_editor("")
#         ide_file = ModelFile()
#         self.current_idefile = ide_file

        self._set_status(ViewMenu.STATUS_FILE_OPEN)

    def ide_open_file(self, widget, path=None):
        '''
        如果已经打开文件，关闭当前文件
        显示“挑选”文件。
        然后显示打开的文件。
        path:string:绝对路径。
        '''
        result = self.RLT_CANCEL

        if(path is None):
            dialog = Gtk.FileChooserDialog("请选择一个文件", self,
                    Gtk.FileChooserAction.OPEN,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

            self._add_filters(dialog)

            response = dialog.run()

            file_path = dialog.get_filename()
            dialog.destroy()
        else:
            response = Gtk.ResponseType.OK
            file_path = path

        if response == Gtk.ResponseType.OK:
            logging.debug("File selected: %s " % file_path)

#             self.multiEditors.show_editor(file_path)
#
#             view_editor = self.multiEditors.get_editor_by_path(file_path)
#             self._ide_search_init(view_editor.editor.get_buffer())
#
#             # 分析标记
#             if self.cur_prj is not None:
#                 tags = self.cur_prj.query_tags_by_file(file_path)
#                 self.ide_refresh_file_tag_list(tags)
            # self.ide_switch_page(file_path)
            self._ide_open_page(file_path)

            result = self.RLT_OK

        elif response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancel to open one file.")
            result = self.RLT_CANCEL

        self._set_status(ViewMenu.STATUS_FILE_OPEN)

        # 设定单词补全。
        self._ide_set_completion(self.cur_prj)

        return result

    def ide_close_file(self, widget):
        '''
        如果打开了文件，
            如果文件已经修改过，保存当前的文件。
            关闭当前的文件。
            清除当前的Buffer。
        \return RLT_XXX
        '''
        logging.debug("close file.")

        ide_editor = self.multiEditors.get_current_ide_editor()
        if ide_editor is None or ide_editor.ide_file is None:
            logging.debug('No file is being opened')
            return self.RLT_OK

        needSave = False

        # 根据是否被修改了，询问是否需要保存。
        if ide_editor.editor.get_buffer().get_modified():
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION, \
                                       Gtk.ButtonsType.YES_NO, "文件已经被改变，是否保存？")
            response = dialog.run()
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                needSave = True

        # 需要保存，就保存，如果不需要，就直接关闭。
        if needSave:
            result = self.ide_save_file(widget)
            if result != self.RLT_OK:
                return result

        # 关闭文件
        self.multiEditors.close_editor(self.multiEditors.get_current_abs_file_path())

        self._set_status(ViewMenu.STATUS_FILE_NONE)

        return self.RLT_OK

    def ide_save_file(self, widget):
        '''
        如果当前文件已经打开，并且已经修改了，就保存文件。
        '''

        logging.debug('ide save file')

        ide_editor = self.multiEditors.get_current_ide_editor()
        if ide_editor is None:
            logging.debug('No file is being opened.')
            return self.RLT_OK

        src_buffer = ide_editor.editor.get_buffer()
        if src_buffer.get_modified():
            if ide_editor.ide_file.file_path is None:
                dialog = Gtk.FileChooserDialog("请选择一个文件", self,
                           Gtk.FileChooserAction.SAVE ,
                           (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                Gtk.STOCK_OK, Gtk.ResponseType.OK))

                response = dialog.run()
                file_path = dialog.get_filename()
                dialog.destroy()

                if response == Gtk.ResponseType.OK:
                    logging.debug("File selected: " + file_path)

                    # 打开一个空的文件，或者里面已经有内容了。
                    ide_editor.ide_file.open_file(file_path)
                    self._set_src_language(src_buffer, file_path)

                elif response == Gtk.ResponseType.CANCEL:
                    logging.debug("Cancel to save one file.")
                    return self.RLT_CANCEL

            # 将内容保存到文件中。
            ide_editor.ide_file.save_file(self._ide_get_editor_buffer())
            src_buffer.set_modified(False)
            logging.debug('ide save file to disk file.')

            # 重新整理TAGS
            self.cur_prj.prepare()

            # 右边的TAG更新
            self._ide_query_tags_by_file_and_refresh(ide_editor.ide_file.file_path)

        self._set_status(ViewMenu.STATUS_FILE_OPEN)

        return self.RLT_OK

    def ide_save_as_file(self, widget):
        '''
        显示对话框，选择另存为的文件名字。
        然后关闭当前文件，
        创建新的Ide文件，打开这个文件，并保存。
        '''
        logging.debug("ide save as other file.")

        ide_editor = self.multiEditors.get_current_ide_editor()
        old_file_path = self.multiEditors.get_current_abs_file_path()

        if ide_editor.ide_file == None:
            logging.debug('No file is being opened')
            return self.RLT_OK

        # 如果是新文件，则按照Save的逻辑进行
        src_buffer = self._ide_get_editor_buffer()
        if src_buffer.get_modified():
            if ide_editor.ide_file.file_path is None:
                return self.ide_save_file(widget)

        # 如果是已经打开的文件，就将当前文件保存成新文件后，关闭旧的，打开新的。
        # 设定新的文件路径
        dialog = Gtk.FileChooserDialog("请选择一个文件", self, \
                                               Gtk.FileChooserAction.SAVE , \
                                               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, \
                                                Gtk.STOCK_OK, Gtk.ResponseType.OK))

        response = dialog.run()
        file_path = dialog.get_filename()
        dialog.destroy()

        if response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancel to save as one file.")
            return self.RLT_CANCEL

        logging.debug("File selected: " + file_path)

        # 将当前文件保存成新文件
        shutil.copy(old_file_path, file_path)

        # 关闭原来的文件。
        # ide_editor.ide_file.close_file()
        self.multiEditors.close_editor(old_file_path)

        # 打开指定的文件，并保存
        # self.current_idefile = ModelFile()
#         ide_editor.ide_file.open_file(file_path)
#
#         ide_editor = self.multiEditors.get_current_ide_editor()
#         src_buffer = self._ide_get_editor_buffer()
#         self.current_idefile.save_file(src_buffer)
#         self._set_src_language(src_buffer, file_path)
#         src_buffer.set_modified(False)

        self.multiEditors.show_editor(file_path)

        # 切换当前的状态
        self._set_status(ViewMenu.STATUS_FILE_OPEN)

    def ide_quit(self, widget):
        '''
        如果打开了当前文件，且修改过了，需要保存。
        关闭当前文件。
        退出程序。
        '''

        result = self.ide_close_file(widget)
        if result != self.RLT_OK:
            return result

        Gtk.main_quit()

    def ide_edit_redo(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()
        if src_buffer.can_redo():
            src_buffer.redo()

    def ide_edit_undo(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()
        if src_buffer.can_undo():
            src_buffer.undo()

    def ide_edit_cut(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().cut_clipboard(clipboard, True)

    def ide_edit_copy(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().copy_clipboard(clipboard)

    def ide_edit_paste(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().paste_clipboard(clipboard, None, True)

    def ide_edit_select_all(self, widget):
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()
        src_buffer.select_range(src_buffer.get_start_iter(), src_buffer.get_end_iter())

    def ide_edit_delete_line(self):
        # 删除光标所在的行

        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return
        src_buffer = ve_editor.editor.get_buffer()

        (start, end) = self._ide_get_selected_line(ve_editor.editor)
        if start is None or end is None:
            return

        src_buffer.delete(start, end)

    def _ide_get_command_chars(self, language):
        lang_id = language.get_id()
        if  lang_id == "cpp" or lang_id == "hpp":
            commend_chars = "//"
        elif  lang_id == "c" or lang_id == "chdr":  # h文件为什么是chdr?
            commend_chars = "//"
        elif lang_id == "makefile" or lang_id == "sh":
            commend_chars = "#"
        else:
            # 缺省使用#
            commend_chars = "#"

        return commend_chars

    def ide_edit_comment(self):
        # 将选择的行变成“注释”
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()

        (start, end) = self._ide_get_selected_line(ve_editor.editor)
        if start is None or end is None:
            return

        commend_chars = self._ide_get_command_chars(src_buffer.get_language())
        if commend_chars is None:
            # 目前只能处理部分程序的comment。
            return

        # 在每行的开始，加入“//”，因为要修改不止一个地方，所以不能用iter。
        start_line = start.get_line()
        end_line = end.get_line()

        for line in range(start_line, end_line):
            iter_ = src_buffer.get_iter_at_line(line)
            src_buffer.insert(iter_, commend_chars)

    def ide_edit_uncomment(self):
        # 将所在的行从“注释“变成正常代码
        # 将选择的行变成“注释”
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()

        (start, end) = self._ide_get_selected_line(ve_editor.editor)
        if start is None or end is None:
            return

        commend_chars = self._ide_get_command_chars(src_buffer.get_language())
        if commend_chars is None:
            # 目前只能处理部分程序的comment。
            return

        # 需要检索指定行的开始“//”
        comment_search_setting = GtkSource.SearchSettings.new()
        comment_search_setting.set_regex_enabled(True)
        comment_search_setting.set_case_sensitive(True)
        comment_search_setting.set_wrap_around(False)

        comment_search_context = GtkSource.SearchContext.new(src_buffer, comment_search_setting)
        # 注意：不能使用\s，因为这个包括\n\r。
        comment_search_pattern = '(^[\t\v\f]*)(' + commend_chars + ')'
        comment_search_context.get_settings().set_search_text(comment_search_pattern)

        start_iter = start
        mark = src_buffer.create_mark("comment_start", start)
        end_mark = src_buffer.create_mark("comment_end", end)
        while True:
            found, march_start, march_end = comment_search_context.forward(start_iter)
            if (not found) or march_end.compare(src_buffer.get_iter_at_mark(end_mark)) > 0:
                break

            src_buffer.move_mark(mark, march_end)
            # replace 方法的两个Iter必须是匹配文字的开始和结束，不是指定一个搜索范围。
            comment_search_context.replace(march_start, march_end, '\g<1>', -1)

            start_iter = src_buffer.get_iter_at_mark(mark)
            start_iter.forward_line()

        src_buffer.delete_mark(mark)
        src_buffer.delete_mark(end_mark)

    def ide_edit_replace(self):
        # 在项目的文件中查找，不是寻找定义。

        # 看看是否已经选中了单词
        tag_name = self._ide_get_selected_text_or_word()

        isOK, results = FwManager.instance().requestService('dialog.common.two_entry',
                                    {'transient_for':self, 'title':"替换", 'entry1_label':"从", 'text1':tag_name,
                                     'entry2_label':"到", 'text2':""})
        response = results['response']
        replace_from = results['text1']
        replace_to = results['text2']

        if response != Gtk.ResponseType.OK or replace_from is None or replace_from == '' or \
            replace_to is None or replace_to == '':
            return

        self._ide_replace_in_file(replace_from, replace_to)

    def _ide_replace_in_file(self, replace_from, replace_to):
        # 替换当前文件中的文字
        ve_editor = self.multiEditors.get_current_ide_editor()
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()

        replace_search_setting = GtkSource.SearchSettings.new()
        replace_search_setting.set_regex_enabled(True)
        replace_search_setting.set_case_sensitive(True)
        replace_search_setting.set_wrap_around(True)

        replace_search_context = GtkSource.SearchContext.new(src_buffer, replace_search_setting)
        replace_search_context.get_settings().set_search_text(replace_from)

        replace_search_context.replace_all(replace_to, -1)

    def ide_switch_page(self, abs_file_path):
        # abs_file_path string 切换到的文件名字

        self.multiEditors.show_editor(abs_file_path)

        view_editor = self.multiEditors.get_editor_by_path(abs_file_path)
        mdl_file = view_editor.ide_file

        # 初始化检索。
        # - 检索会影响到位置，这里只有在函数结尾再加上定位了。
        self._ide_search_init(view_editor.editor.get_buffer())
        self.ide_menu.set_search_options(mdl_file.file_search_key, mdl_file.file_search_case_sensitive, mdl_file.file_search_is_word)

        # 分析标记
        if self.cur_prj is not None:
            self._ide_query_tags_by_file_and_refresh(abs_file_path)

        # 显示文件的路径。
        self.ide_set_title(abs_file_path)

        # 在文件树那里同步
        self.ideFsTree.show_file(abs_file_path)

    def _ide_query_tags_by_file_and_refresh(self, abs_file_path):

        # ModelTask.execute(self.ide_refresh_file_tag_list,
        #                  self.cur_prj.query_tags_by_file, abs_file_path)
        ModelTask.execute(self.ide_refresh_file_tag_list,
                          self.cur_prj.query_ctags_of_file, abs_file_path)

    def _ide_open_page(self, abs_file_path):
        '''
        abs_file_path string 切换到的文件名字
        '''

        self.multiEditors.show_editor(abs_file_path)

        view_editor = self.multiEditors.get_editor_by_path(abs_file_path)
        self._ide_search_init(view_editor.editor.get_buffer())

        # 分析标记
        if self.cur_prj is not None:
            # tags = self.cur_prj.query_tags_by_file(abs_file_path)
            # self.ide_refresh_file_tag_list(tags)
            # 在switch page时，会引发switch事件，调用ide_switch_page，会重新查询tags。
            pass

        # 显示文件的路径。
        self.ide_set_title(abs_file_path)

        # 在文件树那里同步
        self.ideFsTree.show_file(abs_file_path)

    ###################################
    # # 更加底层的功能
    def _add_filters(self, dialog):
        ''' 给对话框加入过滤器 '''
        # TODO:以后应该可以打开任意文件，然后根据后缀进行判断。
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_c = Gtk.FileFilter()
        filter_c.set_name("C/Cpp/hpp files")
        filter_c.add_mime_type("text/x-c")
        dialog.add_filter(filter_c)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

#         filter_any = Gtk.FileFilter()
#         filter_any.set_name("Any files")
#         filter_any.add_pattern("*")
#         dialog.add_filter(filter_any)

    def _set_src_language(self, src_buffer, file_path):
        manager = GtkSource.LanguageManager()

        if file_path is not None:
            language = manager.guess_language(file_path, None)  # 设定语法的类型
            src_buffer.set_language(language)
        else:
            src_buffer.set_language(None)

        return src_buffer

    def _set_status(self, status):
#         if self.current_idefile is None:
#             self.set_title(self.PROGRAM_NAME)
#         else:
#             if self.current_idefile.file_path is None:
#                 self.set_title(self.PROGRAM_NAME + ' New')
#             else:
#                 self.set_title(self.PROGRAM_NAME + ' ' + self.current_idefile.file_path)
        self.ide_set_title()

    def ide_set_title(self, title=''):
        self.set_title("%s %s:%s" % (self.PROGRAM_NAME, self.cur_prj.prj_name, title))

        # TODO:不让状态变化。
        # self.ide_menu.set_status(status)
        self.ide_menu.set_status(ViewMenu.STATUS_FILE_OPEN_CHANGED)

    def ide_refresh_file_tag_list(self, tags):
        # 根据Tag的列表，更新文件对应的Tag列表
        # tags:[IdeOneTag]:Tag列表。

        self.ideTagList.set_model(tags)
        self.ideTagList.expand_all()

    def ide_goto_line(self, line_number):
        # 跳转到当前文件的行。
        # line_number:int:行号（从1开始）
        # return:Bool:False，以后不再调用，True，以后还会调用。

        if line_number < 1:
            logging.error("Error line number %d" % line_number)
            return False

        # print 'goto line number:', line_number
        text_buf = self._ide_get_editor_buffer()
        it = text_buf.get_iter_at_line(line_number - 1)

        text_buf.place_cursor(it)

        # 设定光标的位置，和什么都没有选中
        text_buf.select_range(it, it)
        # 屏幕滚动到这个地方。
        editor = self.multiEditors.get_current_editor()
        editor.scroll_to_iter(it, 0.25, False, 0.0, 0.5)

        # TODO:这里不是错误，而是给threads_add_idle返回不再继续调用的设定。
        return False

    def ide_editor_set_focus(self):
        ''' 获取焦点(延迟调用) '''
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._ide_editor_set_focus)

    def _ide_editor_set_focus(self):
        ''' 获取焦点 '''
        editor = self.multiEditors.get_current_editor()
        editor.grab_focus()

    def ide_goto_file_line(self, file_path, line_number, record=True):

        # 记录的当前的位置
        if record:
            self._ide_push_jumps()

        ''' 跳转到指定文件的行。 '''
        # 先找到对应的文件
        # 然后再滚动到指定的位置
        # print 'jump to path:' + file_path + ', line:' + str(line_number)
        if self.ide_open_file(None, file_path) == self.RLT_OK:
            # 注意：这里采用延迟调用的方法，来调用goto_line方法，可能是buffer被设定后，
            # 还有其他的控件会通过事件来调用滚动，所以才造成马上调用滚动不成功。
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.ide_goto_line, line_number)

    def _in_show_dialog_one_entry(self, title, label):
        isOK, results = FwManager.instance().requestService('dialog.common.one_entry',
                                    {'transient_for':self, 'title':title, 'entry_label':label})
        return results['response'], results['text']

    def ide_find_defination_by_dialog(self):
        ''' 查找定义 '''
        response, tag_name = self._in_show_dialog_one_entry("检索一个TAG", '名字')
        if response != Gtk.ResponseType.OK or tag_name is None or tag_name == '':
            return

        self._ide_search_defination(tag_name)

    def ide_search_defination(self):
        ''' 查找定义 '''
        tag_name = self._ide_get_selected_text_or_word()
        self._ide_search_defination(tag_name)

    def _ide_search_defination(self, tag_name):

        ModelTask.execute(self._after_ide_search_defination,
                          self.cur_prj.query_defination_tags, tag_name)

    def _after_ide_search_defination(self, tag_name, tags):

        if len(tags) == 0:
            info = "没有找到对应\"" + tag_name + "\"的定义。"
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, \
                                       Gtk.ButtonsType.OK, info)
            dialog.run()
            dialog.destroy()

        else:
            self.searchTagList.set_model(tags, self.cur_prj)
            if len(tags) == 1:
                ''' 直接跳转。 '''
                tag = tags[0]
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def ide_search_reference(self):
        ''' 查找引用
        '''
        tag_name = self._ide_get_selected_text_or_word()

        ModelTask.execute(self._after_ide_search_reference,
                          self.cur_prj.query_reference_tags, tag_name)

    def _after_ide_search_reference(self, tag_name, tags):
        if len(tags) == 0:
            info = "没有找到对应\"" + tag_name + "\"的引用。"
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO, \
                                       Gtk.ButtonsType.OK, info)
            dialog.run()
            dialog.destroy()
        else:
            self.searchTagList.set_model(tags, self.cur_prj)
            if len(tags) == 1:
                # 直接跳转。
                tag = tags[0]
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def ide_search_back_tag(self):
        # 回退到上一个位置。
        self._ide_pop_jumps()

    def _svc_add_bookmark(self):
        ''' 【服务】根据当前情况加入新的bookmark。
        '''
        bookmark = self._ide_make_bookmark()
        self.cur_prj.add_bookmark(bookmark)
        return True, {'bookmarks':self.cur_prj.bookmarks, 'current_project': self.cur_prj}

    def ide_jump_to_line(self, widget):
        # 显示一个对话框，输入需要跳转的行。
        response, text = self._in_show_dialog_one_entry("跳转到行", '行')
        if response != Gtk.ResponseType.OK or text is None or text == '':
            return

        if text.isdigit():
            line_number = int(text)
        else:
            line_number = -1

        if line_number != -1:
            self.ide_jump_to(line_number)

    def ide_jump_to(self, line_number):

        # 记录当前的位置
        self._ide_push_jumps()

        self.ide_goto_line(line_number)

    def ide_find(self, search_entry):
        # 如果当前编辑器中有选中的文字，就将此文字放入检索本中。
        # search_text string 需要检索的文字

        view_editor = self.multiEditors.get_current_ide_editor()
        if view_editor is None:
            return

        buf = view_editor.editor.get_buffer()

        if not buf.get_has_selection():
            return

        (start, end) = buf.get_selection_bounds()

        text = buf.get_text(start, end, False)

        # TODO 算是临时方案，首先设定为“”，然后再设定为需要的检索文字，这样就可以100%引发text_changed事件。
        search_entry.set_text("")
        search_entry.set_text(text)

    def _ide_search_init(self, text_buffer):

        self.search_setting = GtkSource.SearchSettings.new()
        self.search_setting.set_regex_enabled(True)
        self.search_setting.set_case_sensitive(True)
        self.search_setting.set_at_word_boundaries(False)
        self.search_setting.set_wrap_around(True)
        # Setting 这里设置后，等真的搜索时，会重新设置setting的某些值，这里的只是缺省设置。

        self.search_context = GtkSource.SearchContext.new(text_buffer, self.search_setting)

        self.search_context.set_highlight(True)

    def _ide_search_text(self, view_editor, need_jump, search_text, need_case_sensitive, search_is_word=False):

        text_buffer = view_editor.editor.get_buffer()

        self.search_context.get_settings().set_search_text(search_text)
        self.search_context.get_settings().set_case_sensitive(need_case_sensitive)
        self.search_context.get_settings().set_at_word_boundaries(search_is_word)

        # - 将目前的检索选项保存到 ModelFile中。
        mdl_file = view_editor.ide_file
        mdl_file.file_search_key = search_text
        mdl_file.file_search_case_sensitive = need_case_sensitive
        mdl_file.file_search_is_word = search_is_word
        logging.debug("save-------------------> %s, %d, %d" % (mdl_file.file_search_key, mdl_file.file_search_case_sensitive, mdl_file.file_search_is_word))

        # 不需要跳转，就退出。
        if not need_jump:
            return

        # -从当前的位置查找
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)

        found, start_iter, end_iter = self.search_context.forward(ite)

        # 如果找到，就跳转到下面最近位置
        if found:
            line_num = start_iter.get_line()
            self.ide_jump_to(line_num)

    def _ide_search_text_next(self, text_buffer, search_text):
        # search_text 是无用的。

        # -从新位置查找
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)

        found, start_iter, end_iter = self.search_context.forward(ite)

        # 如果找到，就跳转到下面最近位置
        if found:
            line_num = start_iter.get_line()
            self.ide_jump_to(line_num)

            text_buffer.move_mark_by_name("selection_bound", start_iter)
            text_buffer.move_mark_by_name("insert", end_iter)

    def ide_find_text(self, need_jump, search_text, need_case_sensitive, search_is_word=False):
        view_editor = self.multiEditors.get_current_ide_editor()
        if view_editor is None:
            return

        self._ide_search_text(view_editor, need_jump, search_text, need_case_sensitive, search_is_word)

    def ide_find_next(self, search_text):
        '''
        如果当前编辑器中有选中的文字，则直接显示对话框。
        对话框中的文字，缺省被选中，可以被全文粘贴。
        然后查找定义。 
        search_text string 需要检索的文字
        '''
        view_editor = self.multiEditors.get_current_ide_editor()
        if view_editor is None:
            return

        self._ide_search_text_next(view_editor.editor.get_buffer(), search_text)

    def ide_find_in_files(self):
        ''' 在项目的文件中查找，不是寻找定义。 '''
        response, pattern = self._in_show_dialog_one_entry("在文件中检索", '模式')
        if response != Gtk.ResponseType.OK or pattern is None or pattern == '':
            return

        self._ide_grep_in_files(pattern)

    def _ide_grep_in_files(self, pattern):
        # 执行检索
        ModelTask.execute_with_spinner(None, self._after_ide_grep_in_files,
                          self.cur_prj.query_grep_tags, pattern, False)

    def _after_ide_grep_in_files(self, tags):
        if len(tags) == 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, "没有找到对应的定义。")
            dialog.run()
            dialog.destroy()

        else:
            self.searchTagList.set_model(tags, self.cur_prj)
            if len(tags) == 1:
                ''' 直接跳转。 '''
                tag = tags[0]
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def ide_find_path(self):
        # 检索需要的文件路径
        response, pattern = self._in_show_dialog_one_entry("检索文件路径", '模式')
        if response != Gtk.ResponseType.OK or pattern is None or pattern == '':
            return

        self._ide_find_path(pattern)

    def _ide_find_path(self, pattern):

        ModelTask.execute(self._after_ide_find_path,
                          self.cur_prj.query_grep_filepath, pattern, False)

    def _after_ide_find_path(self, tags):
        if len(tags) == 0:
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
                                       Gtk.ButtonsType.OK, "没有找到对应的定义。")
            dialog.run()
            dialog.destroy()

        else:
            self.searchTagList.set_model(tags, self.cur_prj)
            if len(tags) == 1:
                # 直接跳转。
                tag = tags[0]
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def _ide_get_selected_line(self, textview):
        # 得到当前光标所在的行/或者选择的多行的 行范围

        src_buffer = textview.get_buffer()
        selection = src_buffer.get_selection_bounds()

        if len(selection) > 0:
            # 已经有选中的文字。
            start, end = selection

            textview.backward_display_line_start(start)
            if not textview.forward_display_line(end):
                textview.forward_display_line_end(end)

            return (start, end)
        else:

            # 没有选中任何的文字
            mark = src_buffer.get_insert()
            start = src_buffer.get_iter_at_mark(mark)
            end = start.copy()

            # textview.backward_display_line(start)        # 到上一行的结尾
            # textview.backward_display_line_start(start) # 到所在行的行首
            # textview.forward_display_line(end)          # 到下一行的开始
            # textview.forward_display_line_end(end)     # 到所在行的结尾
            if textview.forward_display_line(end):
                textview.backward_display_line_start(start)
            else:
                textview.backward_display_line(start)

            return (start, end)

    def _ide_is_not_word(self, txt):
        return not self.word_pattern.match(txt)

    def _ide_get_selected_text_or_word(self):
        ''' 从编辑器中得到当前被选中的文字，
        如果没有就返回光标所在的单词，
        如果都无法达到，就返回None 
        '''
        text_buf = self._ide_get_editor_buffer()
        selection = text_buf.get_selection_bounds()

        text = None
        if len(selection) > 0:
            # 已经有选中的文字。
            start, end = selection
            text = text_buf.get_text(start, end, False)
        else:

            # 没有选中任何的文字
            mark = text_buf.get_insert()
            word_start = text_buf.get_iter_at_mark(mark)
            word_end = text_buf.get_iter_at_mark(mark)

            # 得到以空格为区分的单词开头。
            while True:
                # 获得前一个字符，如果是“_”就前移。
                n = word_start.copy()
                if not n.backward_char():
                    break
                txt = text_buf.get_text(n, word_start, False)
                if self._ide_is_not_word(txt):
                    break

                word_start.backward_char()

            # 得到以空格为区分的单词结尾。
            while True:
                n = word_end.copy()
                if not n.forward_char():
                    break
                txt = text_buf.get_text(word_end, n, False)
                if self._ide_is_not_word(txt):
                    break

                word_end.forward_char()

            text = text_buf.get_text(word_start, word_end, False)

        logging.debug('selected text or word is "%s"' % text)

        return text

    def _ide_make_bookmark(self):
        # 根据当前编辑器的当前光标位置，生成一个bookmark
        # return:ModelTag:书签

        text_buf = self._ide_get_editor_buffer()

        # 得到书签名字
        name = self._ide_get_selected_text_or_word()
        if name is None:
            # 就用
            name = "None"

        # 得到文件
        path = self.multiEditors.get_current_abs_file_path()

        # 得到行号
        mark = text_buf.get_insert()
        location = text_buf.get_iter_at_mark(mark)
        line_no = location.get_line() + 1

        # 得到内容
        line_start = text_buf.get_iter_at_line(line_no - 1)
        line_end = line_start.copy()
        line_end.forward_to_line_end()
        content = text_buf.get_text(line_start, line_end, False)

        return ModelTag(name, path, line_no, content)

    def _ide_set_completion(self, ideProject):
        ''' 设定当前的编辑器的单词补足，当切换不同的Project时，才有必要 '''

        # 单词补齐，使用CompletionWords

        # 配置单词自动补齐，使用自定义的CompletionProvider
        editor = self.multiEditors.get_current_editor()
        completion = editor.props.completion

        # 清除之前的所有provider
        providers = completion.get_providers()
        for p in providers:
            completion.remove_provider(p)

        # 加入新的Provider
        completion.add_provider(ideProject.get_completion_provider())

    def _ide_get_editor_buffer(self):
        editor = self.multiEditors.get_current_editor()
        if editor is None:
            return None

        return editor.get_buffer()

    def _ide_push_jumps(self):
        # 记录当前的位置
        editor = self.multiEditors.get_current_editor()
        if editor is None:
            return

        ide_file = self.multiEditors.get_current_ide_file()
        if ide_file is None:
            return

        text_buffer = editor.get_buffer()
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)

        self.jumps.append((ide_file.file_path, ite.get_line() + 1))

    def _ide_pop_jumps(self):
        # 恢复到原来的位置

        editor = self.multiEditors.get_current_editor()
        if editor is None:
            return

        if len(self.jumps) == 0:
            return

        file_path, line_no = self.jumps.pop()
        self.ide_goto_file_line(file_path, line_no, record=False)

    def _ide_init_ternimal(self):
        if hasattr(self.terminal, "spawn_sync"):  # 2.91
            self.terminal.spawn_sync(
                Vte.PtyFlags.DEFAULT,  # default is fine
                self.cur_prj.src_dirs[0],
                ["/bin/bash"],  # where is the emulator?
                [],  # it's ok to leave this list empty
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,  # at least None is required
                None,
                )
        else:  # < 2.90
            self.terminal.fork_command_full(
                Vte.PtyFlags.DEFAULT,  # default is fine
                self.cur_prj.src_dirs[0],
                ["/bin/bash"],  # where is the emulator?
                [],  # it's ok to leave this list empty
                GLib.SpawnFlags.DO_NOT_REAP_CHILD,
                None,  # at least None is required
                None,
                )
