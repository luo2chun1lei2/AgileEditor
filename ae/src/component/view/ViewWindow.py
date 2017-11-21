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
    # 返回值的定义
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
            {'name':'view.main.refresh_project', 'help': 'refresh the project file-tree and tags.'},
            {'name':'view.main.goto_line', 'help': 'goto the given line and focus on editor.'},
            {'name':'view.main.get_current_project', 'help': 'get current project.'},  # TODO
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

        elif serviceName == "view.main.make_bookmark":
            return self._svc_add_bookmark()

        elif serviceName == 'view.main.open_file':
            rlt = self.ide_open_file(params['abs_file_path'])
            return True, {'result': rlt}

        elif serviceName == 'view.main.refresh_project':
            self.ide_update_tags_of_project()
            return True, None

        elif serviceName == 'view.main.get_current_project':
            return True, {'project':self.cur_prj}

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
            self._ide_open_prj(prj)

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
            self.ide_open_file()
        elif action == ViewMenu.ACTION_FILE_CLOSE:
            self.ide_close_file(widget)
            self.ide_new_file(widget)
        elif action == ViewMenu.ACTION_FILE_SAVE:
            self.ide_save_file(widget)
        elif action == ViewMenu.ACTION_FILE_SAVE_AS:
            self.ide_save_as_file(widget)

        # 检索
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
            FwManager.instance().requestService('view.fstree.set_dir', {'dir':prj.src_dirs[0]})

        # 设置窗口标题。
        self.ide_set_title("")

        # 设置终端属性。
        FwManager.instance().requestService('view.terminal.init', {'dir':self.cur_prj.src_dirs[0]})
        return True

    def ide_preferences_project(self):
        # 配置当前的项目
        # 设定保存在workshop的数据模型之中。
        setting = {'style': self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_STYLE],
                   'font': self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_FONT] }
        isOK, results = FwManager.instance().requestService('dialog.project.setting',
                        {'parent':self, 'setting':setting})
        setting = results['setting']
        if setting is None:
            return

        # 修改系统设定！
        FwManager.instance().requestService('view.multi_editors.change_editor_style', {'style': setting['style']})
        FwManager.instance().requestService('view.multi_editors.change_editor_font', {'font': setting['font']})

        self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_STYLE] = setting['style']
        self.ideWorkshop.setting[ModelWorkshop.OPT_NAME_FONT] = setting['font']

        self.ideWorkshop.save_conf()

    def ide_close_project(self):
        ''' 关闭当前的项目 '''
        self._set_status(ViewMenu.STATUS_PROJECT_NONE)

    def ide_update_tags_of_project(self):
        # 更新当前项目的TAGS，并且更新文件列表。
        if self.cur_prj is None:
            return

        # 更新当前项目的文件列表
        FwManager.instance().requestService('view.fstree.set_dir', {'dir':self.cur_prj.src_dirs[0]})

        # 更新右边的TAGS
        self.cur_prj.prepare()

    def ide_new_file(self, widget):
        '''
        产生一个没有路径的项目文件。
        TODO:还没有决定如何实现！
        '''
        self._set_status(ViewMenu.STATUS_FILE_OPEN)

    def ide_open_file(self, path=None):
        '''
        如果已经打开文件，变为当前文件。如果路径是空，就显示“挑选”文件。然后打开此文件。
        @param path:string:绝对路径。
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

        ide_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
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
        abs_file_path = FwManager.requestOneSth('abs_file_path', 'view.multi_editors.get_current_abs_file_path')
        FwManager.instance().requestService('view.multi_editors.close_editor', {'abs_file_path': abs_file_path})

        # 关闭文件的tag列表。
        FwManager.instance().requestService('view.file_taglist.show_taglist', {'taglist': []})

        self._set_status(ViewMenu.STATUS_FILE_NONE)

        return self.RLT_OK

    def ide_save_file(self, widget):
        '''
        如果当前文件已经打开，并且已经修改了，就保存文件。
        '''

        logging.debug('ide save file')

        ide_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
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
            ide_editor.ide_file.save_file(UtilEditor.get_editor_buffer())
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

        ide_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        old_file_path = FwManager.requestOneSth('abs_file_path', 'view.multi_editors.get_current_abs_file_path')

        if ide_editor.ide_file == None:
            logging.debug('No file is being opened')
            return self.RLT_OK

        # 如果是新文件，则按照Save的逻辑进行
        src_buffer = UtilEditor.get_editor_buffer()
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
        FwManager.instance().requestService('view.multi_editors.close_editor', {'abs_file_path': old_file_path})

        # 打开指定的文件，并保存
        FwManager.instance().requestService('view.multi_editors.open_editor', {'abs_file_path': file_path})

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
        ModelTask.execute(self.ide_refresh_file_tag_list,
                          self.cur_prj.query_ctags_of_file, abs_file_path)

    def _ide_open_page(self, abs_file_path):
        '''
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
        FwManager.instance().requestService('view.file_taglist.show_taglist', {'taglist':tags})

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

    def ide_find_defination_by_dialog(self):
        ''' 查找定义 '''
        response, tag_name = UtilDialog.show_dialog_one_entry("检索一个TAG", '名字')
        if response != Gtk.ResponseType.OK or tag_name is None or tag_name == '':
            return

        self._ide_search_defination(tag_name)

    def ide_search_defination(self):
        ''' 查找定义 '''
        tag_name = UtilEditor.get_selected_text_or_word()
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
            FwManager.instance().requestService('view.search_taglist.show_taglist', {'taglist':tags, 'project':self.cur_prj})
            if len(tags) == 1:
                ''' 直接跳转。 '''
                tag = tags[0]
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def ide_search_reference(self):
        ''' 查找引用
        '''
        tag_name = UtilEditor.get_selected_text_or_word()

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
            FwManager.instance().requestService('view.search_taglist.show_taglist', {'taglist':tags, 'project':self.cur_prj})
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
        bookmark = UtilEditor.make_bookmark()
        self.cur_prj.add_bookmark(bookmark)
        return True, {'bookmarks':self.cur_prj.bookmarks, 'current_project': self.cur_prj}



    def ide_find_path(self):
        # 检索需要的文件路径
        response, pattern = UtilDialog.show_dialog_one_entry("检索文件路径", '模式')
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
            FwManager.instance().requestService('view.search_taglist.show_taglist', {'taglist':tags, 'project':self.cur_prj})
            if len(tags) == 1:
                # 直接跳转。
                tag = tags[0]
                self.ide_goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def _ide_set_completion(self, ideProject):
        ''' 设定当前的编辑器的单词补足，当切换不同的Project时，才有必要 '''

        # 单词补齐，使用CompletionWords

        # 配置单词自动补齐，使用自定义的CompletionProvider
        editor = FwManager.requestOneSth('editor', "view.multi_editors.get_current_editor")
        completion = editor.props.completion

        # 清除之前的所有provider
        providers = completion.get_providers()
        for p in providers:
            completion.remove_provider(p)

        # 加入新的Provider
        completion.add_provider(ideProject.get_completion_provider())



    def _ide_pop_jumps(self):
        # 恢复到原来的位置
        isOK, results = FwManager.instance().requestService('model.jump_history.pop')
        if results is None:
            return
        self.ide_goto_file_line(results['file_path'], results['line_no'], record=False)
