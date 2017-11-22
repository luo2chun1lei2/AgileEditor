# -*- coding:utf-8 -*-

#######################################
# 编辑器窗口
# 1, 顶部是菜单和工具栏（内容都随着选中的对象而定）。
# 2, 项目浏览器
# 3, 编辑器，使用GtkSourceView。
# 4, 代码浏览工具。
# 5, 编译和调试工具。
# 6, 命令工具（可以编写任意的命令）

import os, shutil, re, logging
from gi.repository import Gtk, Gdk, GtkSource, GLib

from framework.FwManager import FwManager

from component.model.ModelWorkshop import ModelWorkshop
from component.model.ModelTask import ModelTask
from component.view.ViewMenu import ViewMenu
from component.model.ModelTags import ModelTag
from component.util.UtilEditor import UtilEditor
from component.util.UtilDialog import UtilDialog

from framework.FwComponent import FwComponent

class ViewWindow(Gtk.Window, FwComponent):

    # ideWorkshop:ModelWorkshop:当前的workshop。
    # cur_prj:ModelProject:当前打开的项目。

    ###################################
    # 返回值的定义 TODO 移动到更加通用的类中。
    RLT_OK = 0
    RLT_CANCEL = 1  # 取消
    RLT_ERROR = 2  # 错误

    # 主窗口的标题。
    PROGRAM_NAME = 'AgileEditor v0.3 - '

    # override component
    def onRegistered(self, manager):
        # 将已经生成好的控件作为组件注册到框架中。
        FwManager.instance().load("view_menu", self.ide_menu)

        info = [
            {'name':'view.main.get_window', 'help':'get the main window.'},
            {'name':'view.main.show_bookmark', 'help':'show a bookmark.'},
            {'name':'view.main.make_bookmark', 'help': 'make one bookmark by current position, and return bookmarks list'},
            {'name':'view.main.open_file', 'help': 'show a file by absolutive file path.'},  # TODO
            {'name':'view.main.close_files', 'help': 'close opened files.'},  # TODO
            {'name':'view.main.goto_line', 'help': 'goto the given line and focus on editor.'},
            {'name':'view.main.get_current_project', 'help': 'get current project.'},  # TODO
            {'name':'view.main.set_current_project', 'help': 'set current project.'},  # TODO
            {'name':'view.main.get_current_workshop', 'help': 'get current workshop.'},  # TODO
            {'name':'view.main.set_title', 'help': 'set title of window.'},
            {'name':'view.main.close_current_project', 'help': 'close the current project.'},
            {'name':'view.main.set_status', 'help': 'set status of window.'},  # TODO
            ]
        manager.registerService(info, self)

        # register listening event.
        manager.register_event_listener('view.multi_editors.switch_page', self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "view.main.show_bookmark":  # 显示一个bookmark
            tag = params['tag']  # ModelTag
            self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)
            self.ide_editor_set_focus()
            return (True, None)

        elif serviceName == "view.main.set_title":
            self.ide_set_title(params['title'])
            return (True, None)
        elif serviceName == "view.main.set_status":
            self._set_status(params['status'])
            return (True, None)

        elif serviceName == "view.main.make_bookmark":
            return self._svc_add_bookmark()

        elif serviceName == 'view.main.open_file':
            rlt = self.ide_open_file(params['abs_file_path'])
            return True, {'result': rlt}
        elif serviceName == 'view.main.close_files':
            # TODO 实现是错误的，没有关闭所有的文件!只关闭了当前的！
            isOK, results = FwManager.instance().requestService('ctrl.file.close')
            rlt = results['result']
            return True, {'result':rlt}

        elif serviceName == 'view.main.get_current_project':
            return True, {'project':self.cur_prj}
        elif serviceName == 'view.main.set_current_project':
            self.cur_prj = params['project']
            return True, None
        elif serviceName == 'view.main.close_current_project':
            self.ide_close_project()
            return True, None
        elif serviceName == 'view.main.get_current_workshop':
            return True, {'workshop':self.ideWorkshop}

        elif serviceName == 'view.main.goto_line':
            # 跳转到对应的行。

            if 'file_path' in params:
                self.ide_goto_file_line(params['file_path'], params['line_no'])
            else:
                UtilEditor.goto_line(params['line_no'])

            # 其他控件发送过来此信息后，需要让编辑器获取焦点。
            self.ide_editor_set_focus()
            return True, None

        elif serviceName == 'view.main.get_window':
            return (True, {'window': self})
        else:
            return (False, None)

    # override FwListener
    def on_listened(self, event_name, params):
        if event_name == 'view.multi_editors.switch_page':
            self.ide_switch_page(params['abs_file_path'])
            return True
        else:
            return False

    ''' 主窗口。 '''
    def __init__(self, workshop, prj, want_open_file):

        self.cur_prj = None
        self.last_search_pattern = None

        # 读取workshop的信息。

        self.ideWorkshop = workshop

        # 创建画面
        self._create_layout()

        # 初始化状态
        if prj:
            pass

        if want_open_file:
            path = os.path.abspath(want_open_file)
            self.ide_open_file(path)

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

        # 保存项目用的各种列表的Notebook
        self.nbPrj = Gtk.Notebook()
        self.nbPrj.set_scrollable(True)

        ###################################################
        # 布局
        # resize:子控件是否跟着paned的大小而变化。
        # shrink:子控件是否能够比它需要的大小更小。
        panedEdtiorAndTagList = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        view = FwManager.requestOneSth('view', 'view.multi_editors.get_view')
        panedEdtiorAndTagList.pack1(view, resize=True, shrink=True)
        view = FwManager.requestOneSth('view', 'view.file_taglist.get_view')
        panedEdtiorAndTagList.pack2(view, resize=False, shrink=True)

        view = FwManager.requestOneSth('view', 'view.search_taglist.get_view')
        self.nbPrj.append_page(view, Gtk.Label("检索"))
        view = FwManager.requestOneSth('view', 'view.bookmarks.get_view')
        self.nbPrj.append_page(view, Gtk.Label("书签"))
        view = FwManager.requestOneSth('view', 'view.terminal.get_view')
        self.nbPrj.append_page(view, Gtk.Label("控制台"))

        panedEdtiorAndSearchTag = Gtk.Paned.new(Gtk.Orientation.VERTICAL)
        panedEdtiorAndSearchTag.pack1(panedEdtiorAndTagList, resize=True, shrink=True)
        panedEdtiorAndSearchTag.pack2(self.nbPrj, resize=False, shrink=True)

        panedFsAndEditor = Gtk.Paned.new(Gtk.Orientation.HORIZONTAL)
        view = FwManager.requestOneSth('view', 'view.fstree.get_view')
        panedFsAndEditor.pack1(view, resize=False, shrink=True)
        panedFsAndEditor.pack2(panedEdtiorAndSearchTag, resize=True, shrink=True)
        panedFsAndEditor.set_position(200);

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox.pack_start(self.ide_menu.menubar, False, False, 0)
        vbox.pack_start(self.ide_menu.toolbar, False, False, 0)
        vbox.pack_start(panedFsAndEditor, True, True, 5)

        self.add(vbox)

    ###################################
    # # 创建画面

    def create_src_list(self):
        # 显示分析结果的列表
        pass

    ###################################
    # # 回调方法
    def on_menu_func(self, widget, action, param=None, param2=None, param3=None, param4=None):

        if action == ViewMenu.ACTION_FILE_OPEN:
            self.ide_open_file()

        elif action == ViewMenu.ACTION_EDITOR_SWITCH_PAGE:
            self.ide_switch_page(param)

        else:
            logging.error('Unknown action %d' % action)

    def on_src_bufer_changed(self, widget):
        ''' 当文件发了变化后。'''
        self._set_status(ViewMenu.STATUS_FILE_OPEN_CHANGED)

    ###################################
    # # 基本功能

    def ide_close_project(self):
        ''' 关闭当前的项目 TODO 什么都没有实现！'''
        self._set_status(ViewMenu.STATUS_PROJECT_NONE)

    def ide_new_file(self):
        '''
        产生一个没有路径的项目文件。
        TODO:还没有决定如何实现！
        '''
        self._set_status(ViewMenu.STATUS_FILE_OPEN)

    def ide_open_file(self, path=None):
        ''' TODO 现在不能删除
        如果已经打开文件，变为当前文件。如果路径是空，就显示“挑选”文件。然后打开此文件。
        @param path:string:绝对路径。
        '''
        result = self.RLT_CANCEL

        if(path is None):
            dialog = Gtk.FileChooserDialog("请选择一个文件", self,
                    Gtk.FileChooserAction.OPEN,
                    (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                     Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

            UtilDialog.add_filters(dialog)

            response = dialog.run()

            file_path = dialog.get_filename()
            dialog.destroy()
        else:
            response = Gtk.ResponseType.OK
            file_path = path

        if response == Gtk.ResponseType.OK:
            logging.debug("File selected: %s " % file_path)
            self._ide_open_page(file_path)

            result = self.RLT_OK

        elif response == Gtk.ResponseType.CANCEL:
            logging.debug("Cancel to open one file.")
            result = self.RLT_CANCEL

        self._set_status(ViewMenu.STATUS_FILE_OPEN)

        # 设定单词补全。
        UtilEditor.set_completion(self.cur_prj)

        return result

    def ide_switch_page(self, abs_file_path):
        # abs_file_path string 切换到的文件名字
        FwManager.instance().requestService('view.multi_editors.open_editor', {'abs_file_path': abs_file_path})

        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_editor_by_path', {'abs_file_path': abs_file_path})
        mdl_file = view_editor.ide_file

        # 初始化检索。
        # - 检索会影响到位置，这里只有在函数结尾再加上定位了。
        FwManager.instance().requestService('ctrl.search.init', {'text_buffer':view_editor.editor.get_buffer()})
        self.ide_menu.set_search_options(mdl_file.file_search_key, mdl_file.file_search_case_sensitive, mdl_file.file_search_is_word)

        # 分析标记
        if self.cur_prj is not None:
            self._ide_query_tags_by_file_and_refresh(abs_file_path)

        # 显示文件的路径。
        self.ide_set_title(abs_file_path)

        # 在文件树那里同步
        FwManager.instance().requestService('view.fstree.focus_file', {'abs_file_path':abs_file_path})

    def _ide_query_tags_by_file_and_refresh(self, abs_file_path):
        # TODO 建议和switch一起移动到CtrlFile中，已经复制了一份“_query_tags_by_file_and_refresh”
        ModelTask.execute(self.ide_refresh_file_tag_list,
                          self.cur_prj.query_ctags_of_file, abs_file_path)

    def ide_refresh_file_tag_list(self, tags):
        # TODO 建议和switch一起移动到CtrlFile中，已经复制了一份“_refresh_file_tag_list”
        # 根据Tag的列表，更新文件对应的Tag列表
        # tags:[IdeOneTag]:Tag列表。
        FwManager.instance().requestService('view.file_taglist.show_taglist', {'taglist':tags})

    def _ide_open_page(self, abs_file_path):
        ''' TODO 已经移植到 CtrlFile 中。
        abs_file_path string 切换到的文件名字
        '''
        FwManager.instance().requestService('view.multi_editors.open_editor', {'abs_file_path': abs_file_path})

        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_editor_by_path', {'abs_file_path': abs_file_path})
        FwManager.instance().requestService('ctrl.search.init', {'text_buffer':view_editor.editor.get_buffer()})

        # 分析标记
        if self.cur_prj is not None:
            # tags = self.cur_prj.query_tags_by_file(abs_file_path)
            # self.ide_refresh_file_tag_list(tags)
            # 在switch page时，会引发switch事件，调用ide_switch_page，会重新查询tags。
            pass

        # 显示文件的路径。
        self.ide_set_title(abs_file_path)

        # 在文件树那里同步
        FwManager.instance().requestService('view.fstree.focus_file', {'abs_file_path':abs_file_path})

    ###################################
    # # 更加底层的功能

    def _set_status(self, status):
        ''' TODO 这个方法需要彻底修改. '''

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

    def ide_editor_set_focus(self):
        ''' 获取焦点(延迟调用) '''
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._ide_editor_set_focus)

    def _ide_editor_set_focus(self):
        ''' 获取焦点 '''
        editor = FwManager.requestOneSth('editor', "view.multi_editors.get_current_editor")
        editor.grab_focus()

    # TODO same with CtrlSearch's goto_file_line, should be removed.
    def ide_goto_file_line(self, file_path, line_number, record=True):

        # 记录的当前的位置
        if record:
            UtilEditor.push_jumps()

        ''' 跳转到指定文件的行。 '''
        # 先找到对应的文件
        # 然后再滚动到指定的位置
        # print 'jump to path:' + file_path + ', line:' + str(line_number)
        if self.ide_open_file(file_path) == self.RLT_OK:
            # 注意：这里采用延迟调用的方法，来调用goto_line方法，可能是buffer被设定后，
            # 还有其他的控件会通过事件来调用滚动，所以才造成马上调用滚动不成功。
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, UtilEditor.goto_line, line_number)

    def _svc_add_bookmark(self):
        ''' 【服务】根据当前情况加入新的bookmark。
        '''
        bookmark = UtilEditor.make_bookmark()
        self.cur_prj.add_bookmark(bookmark)
        return True, {'bookmarks':self.cur_prj.bookmarks, 'current_project': self.cur_prj}
