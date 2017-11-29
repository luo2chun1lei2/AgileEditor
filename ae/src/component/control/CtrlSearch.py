# -*- coding:utf-8 -*-

'''
负责检索和跳转用的。
'''
import logging
from gi.repository import Gdk, GLib, Gtk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

from component.model.ModelTask import ModelTask
from component.util.UtilEditor import UtilEditor
from component.util.UtilDialog import UtilDialog
from component.view.ViewWindow import ViewWindow

class CtrlSearch(FwComponent):
    def __init__(self):
        super(CtrlSearch, self).__init__()
        self.search_setting = None
        self.last_search_pattern = None

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.search.init', 'help':'initialize the search context.'},  # TODO 这里是否是一个服务，还应该是监听事件，应该仔细考虑！
                {'name':'ctrl.search.goto_line', 'help': 'goto the given line and focus on editor.'},
                {'name':'ctrl.search.jump_to', 'help':'Jump to ? line.'},
                {'name':'ctrl.search.find', 'help':'get the selected word and focus on search textbox.'},  # This is NOT direct finding function.
                {'name':'ctrl.search.find_text', 'help':'begin to find text.'},
                {'name':'ctrl.search.find_next', 'help':'find the next matched word.'},
                {'name':'ctrl.search.find_prev', 'help':'find the previous matched word.'},
                {'name':'ctrl.search.find_in_files', 'help':'find the matched word in files.'},
                {'name':'ctrl.search.find_in_files_again', 'help':'find the matched word in files again.'},
                {'name':'ctrl.search.find_path', 'help':'find the match path.'},
                {'name':'ctrl.search.find_definition', 'help':'find the definition of symbol.'},
                {'name':'ctrl.search.find_definition_need_input', 'help':'show dialog to get the symbol, and then find the definition.'},
                {'name':'ctrl.search.find_reference', 'help':'find the reference of symbol.'},
                {'name':'ctrl.search.find_reference_need_input', 'help':'show dialog to get the symbol, and then find the reference.'},
                {'name':'ctrl.search.go_back_tag', 'help':'go back to the previous tag.'},
                {'name':'ctrl.search.update_tags', 'help':'update the tags by newest project status.'},
                {'name':'ctrl.search.show_bookmark', 'help':'show a bookmark.'},
                {'name':'ctrl.search.make_bookmark', 'help': 'make one bookmark by current position, and return bookmarks list'},
                ]
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.search.jump_to":
            self._jump_to_line()
            return (True, None)
        elif serviceName == 'ctrl.search.find':
            self._get_word_and_jump_to_search_box()
            return (True, None)
        elif serviceName == 'ctrl.search.find_text':
            self._find_text(params['need_jump'], params['search_text'], params['need_case_sensitive'], params['need_search_is_word'])
            return (True, None)
        elif serviceName == 'ctrl.search.find_next':
            self._find_next(params['text'])
            return (True, None)
        elif serviceName == 'ctrl.search.find_prev':
            self._find_prev(params['text'])
            return (True, None)
        elif serviceName == 'ctrl.search.init':
            self._search_init(params['text_buffer'])
            return (True, None)
        elif serviceName == 'ctrl.search.find_in_files':
            self._find_in_files()
            return (True, None)
        elif serviceName == 'ctrl.search.find_in_files_again':
            self._find_in_files(self.last_search_pattern)
            return (True, None)
        elif serviceName == 'ctrl.search.find_path':
            self._find_path_with_dialog()
            return (True, None)
        elif serviceName == 'ctrl.search.find_definition':
            self._find_defination()
            return (True, None)
        elif serviceName == 'ctrl.search.find_definition_need_input':
            self._find_defination_by_dialog()
            return (True, None)
        elif serviceName == 'ctrl.search.find_reference':
            self._find_reference()
            return (True, None)
        elif serviceName == 'ctrl.search.find_reference_need_input':
            self._find_reference_by_dialog()
            return (True, None)
        elif serviceName == 'ctrl.search.go_back_tag':
            self._go_back_tag()
            return (True, None)
        elif serviceName == 'ctrl.search.update_tags':
            self._update_tags_of_project()
            return (True, None)
        elif serviceName == "ctrl.search.make_bookmark":
            return self._add_bookmark()
        elif serviceName == "ctrl.search.show_bookmark":  # 显示一个bookmark
            tag = params['tag']  # ModelTag
            self._goto_file_line(tag.tag_file_path, tag.tag_line_no)
            self._editor_set_focus()
            return (True, None)
        elif serviceName == 'ctrl.search.goto_line':
            # 跳转到对应的行。
            if 'file_path' in params:
                self._goto_file_line(params['file_path'], params['line_no'])
            else:
                UtilEditor.goto_line(params['line_no'])

            # 其他控件发送过来此信息后，需要让编辑器获取焦点。
            self._editor_set_focus()
            return True, None
        else:
            return (False, None)

    # override component
    def onSetup(self, manager):

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchJumpTo',
                  'title':None,
                  'accel':"<control>L",
                  'stock_id':Gtk.STOCK_JUMP_TO,
                  'service_name':'ctrl.search.jump_to'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFind',
                  'title':None,
                  'accel':"<control>F",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFindNext',
                  'title':'Find Next',
                  'accel':"<control>G",
                  'stock_id':None,
                  'service_name':'ctrl.search.find_next'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFindPrev',
                  'title':'Find Prev',
                  'accel':"<shift><control>G",
                  'stock_id':None,
                  'service_name':'ctrl.search.find_prev'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFindInFiles',
                  'title':'Find in files',
                  'accel':"<control>H",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find_in_files'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchAgainFindInFiles',
                  'title':'Find in files Again',
                  'accel':"<shift><control>H",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find_in_files_again'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFindPath',
                  'title':'Find path',
                  'accel':"<control>P",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find_path'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchDefinition',
                  'title':'Definition',
                  'accel':"F3",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find_definition'}
        manager.request_service("view.menu.add", params)
        
        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchDefinitionNeedInput',
                  'title':'Definition with Dialog',
                  'accel':"<control>F3",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find_definition_need_input'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchReference',
                  'title':'Reference',
                  'accel':"F4",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find_reference'}
        manager.request_service("view.menu.add", params)
        
        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchReferenceNeedInput',
                  'title':'Reference with Dialog',
                  'accel':"<control>F4",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find_reference_need_input'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchBackTag',
                  'title':'Back Tag',
                  'accel':"<control>Escape",
                  'stock_id':Gtk.STOCK_GO_BACK,
                  'service_name':'ctrl.search.go_back_tag',
                  'in_toolbar':True}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchUpdateTags',
                  'title':'Update Tags',
                  'accel':"F5",
                  'stock_id':Gtk.STOCK_REFRESH,
                  'service_name':'ctrl.search.update_tags',
                  'in_toolbar':True}
        manager.request_service("view.menu.add", params)

        return True

    def _jump_to_line(self):
        from component.util.UtilDialog import UtilDialog

        # 显示一个对话框，输入需要跳转的行。
        response, text = UtilDialog.show_dialog_one_entry("跳转到行", '行')
        if response != Gtk.ResponseType.OK or text is None or text == '':
            return

        if text.isdigit():
            line_number = int(text)
        else:
            line_number = -1

        if line_number != -1:
            UtilEditor.jump_to(line_number)

    def _get_word_and_jump_to_search_box(self):
        # 如果当前编辑器中有选中的文字，就将此文字放入检索文本框中。

        view_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if view_editor is None:
            return

        buf = view_editor.editor.get_buffer()

        if not buf.get_has_selection():
            text = None
        else:
            (start, end) = buf.get_selection_bounds()
            text = buf.get_text(start, end, False)

        FwManager.instance().request_service('view.menu.set_and_jump_to_search_textbox', {'text': text})

    def _find_next(self, search_text):
        '''
        如果当前编辑器中有选中的文字，则直接显示对话框。
        对话框中的文字，缺省被选中，可以被全文粘贴。
        然后查找定义。 
        search_text string 需要检索的文字
        '''
        view_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if view_editor is None:
            return

        self._search_text_next(view_editor.editor.get_buffer(), search_text)

    def _find_prev(self, search_text):
        '''
        如果当前编辑器中有选中的文字，则直接显示对话框。
        对话框中的文字，缺省被选中，可以被全文粘贴。
        然后查找定义。 
        search_text string 需要检索的文字
        '''
        view_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if view_editor is None:
            return

        self._search_text_prev(view_editor.editor.get_buffer(), search_text)

    def _search_text_next(self, text_buffer, search_text):
        # search_text 是无用的。

        # -从新位置查找
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)

        found, start_iter, end_iter = self.search_context.forward(ite)

        # 如果找到，就跳转到下面最近位置
        if found:
            line_num = start_iter.get_line()
            UtilEditor.jump_to(line_num)

            text_buffer.move_mark_by_name("selection_bound", start_iter)
            text_buffer.move_mark_by_name("insert", end_iter)

    def _search_text_prev(self, text_buffer, search_text):
        # search_text 是无用的。

        # -从新位置查找
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)
        # diff : 如果“insert”就在一个匹配的单词后面，向前找就是这个单词了。
        # 这样会导致一直就定位这个位置，无法向前找！ 缺点是用鼠标定位，会跳过紧挨着的上一个单词。
        ite.backward_char()

        found, start_iter, end_iter = self.search_context.backward(ite)  # diff

        # 如果找到，就跳转到下面最近位置
        if found:
            line_num = start_iter.get_line()
            UtilEditor.jump_to(line_num)

            text_buffer.move_mark_by_name("selection_bound", start_iter)
            text_buffer.move_mark_by_name("insert", end_iter)

    def _search_init(self, text_buffer):

        self.search_setting = GtkSource.SearchSettings.new()
        self.search_setting.set_regex_enabled(True)
        self.search_setting.set_case_sensitive(True)
        self.search_setting.set_at_word_boundaries(False)
        self.search_setting.set_wrap_around(True)
        # Setting 这里设置后，等真的搜索时，会重新设置setting的某些值，这里的只是缺省设置。

        self.search_context = GtkSource.SearchContext.new(text_buffer, self.search_setting)

        self.search_context.set_highlight(True)

    def _find_text(self, need_jump, search_text, need_case_sensitive, search_is_word=False):
        view_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if view_editor is None:
            return

        self._search_text(view_editor, need_jump, search_text, need_case_sensitive, search_is_word)

    def _search_text(self, view_editor, need_jump, search_text, need_case_sensitive, search_is_word=False):

        text_buffer = view_editor.editor.get_buffer()

        self.search_context.get_settings().set_search_text(search_text)
        self.search_context.get_settings().set_case_sensitive(need_case_sensitive)
        self.search_context.get_settings().set_at_word_boundaries(search_is_word)

        # - 将目前的检索选项保存到 ModelFile中。
        mdl_file = view_editor.ide_file
        mdl_file.file_search_key = search_text
        mdl_file.file_search_case_sensitive = need_case_sensitive
        mdl_file.file_search_is_word = search_is_word
        logging.debug("save--> %s, %d, %d" % (mdl_file.file_search_key, mdl_file.file_search_case_sensitive, mdl_file.file_search_is_word))

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
            UtilEditor.jump_to(line_num)

    def _find_in_files(self, pattern=None):
        ''' 在项目的文件中查找，不是寻找定义。 '''
        if pattern is None:
            response, pattern = UtilDialog.show_dialog_one_entry("在文件中检索", '模式')
            if response != Gtk.ResponseType.OK or pattern is None or pattern == '':
                return

        self.last_search_pattern = pattern  # 记录最新的检索
        self._grep_in_files(pattern)

    def _grep_in_files(self, pattern):
        # 执行检索
        cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
        ModelTask.execute(self._after_grep_in_files,
                          cur_prj.query_grep_tags, pattern, False)

    def _after_grep_in_files(self, tags):
        if len(tags) == 0:
            FwManager.instance().request_service("dialog.msg.warn", {'message':"没有找到对应的定义。"})

        else:
            cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
            FwManager.instance().request_service('view.search_taglist.show_taglist', {'taglist':tags, 'project':cur_prj})
            if len(tags) == 1:
                ''' 直接跳转。 '''
                tag = tags[0]
                self._goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def _goto_file_line(self, file_path, line_number, record=True):

        # 记录的当前的位置
        if record:
            UtilEditor.push_jumps()

        ''' 跳转到指定文件的行。 '''
        # 先找到对应的文件，然后再滚动到指定的位置
        logging.debug('jump to path:' + file_path + ', line:' + str(line_number))
        isOK, results = FwManager.instance().request_service('ctrl.file.open', {'abs_file_path': file_path})
        if isOK and results['result'] == ViewWindow.RLT_OK:  # TODO 这里需要知道ViewWindow的常亮
            # 注意：这里采用延迟调用的方法，来调用goto_line方法，可能是buffer被设定后，
            # 还有其他的控件会通过事件来调用滚动，所以才造成马上调用滚动不成功。
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, UtilEditor.goto_line, line_number)

    def _find_path_with_dialog(self):
        # 检索需要的文件路径
        response, pattern = UtilDialog.show_dialog_one_entry("检索文件路径", '模式')
        if response != Gtk.ResponseType.OK or pattern is None or pattern == '':
            return

        self._find_path(pattern)

    def _find_path(self, pattern):
        cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
        ModelTask.execute(self._after_find_path,
                          cur_prj.query_grep_filepath, pattern, False)

    def _after_find_path(self, tags):
        if len(tags) == 0:
            FwManager.instance().request_service("dialog.msg.warn", {'message':"没有找到对应的文件路径。"})

        else:
            cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
            FwManager.instance().request_service('view.search_taglist.show_taglist', {'taglist':tags, 'project':cur_prj})
            if len(tags) == 1:
                # 直接跳转。
                tag = tags[0]
                self._goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def _find_defination_by_dialog(self):
        ''' 查找定义 '''
        response, tag_name = UtilDialog.show_dialog_one_entry("查找定义", '名字')
        if response != Gtk.ResponseType.OK or tag_name is None or tag_name == '':
            return

        self._search_defination(tag_name)

    def _find_defination(self):
        ''' 查找定义 '''
        tag_name = UtilEditor.get_selected_text_or_word()
        if tag_name is None:
            self._find_defination_by_dialog()
        else:
            self._search_defination(tag_name)

    def _search_defination(self, tag_name):
        cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
        ModelTask.execute(self._after_search_defination,
                          cur_prj.query_defination_tags, tag_name)

    def _after_search_defination(self, tag_name, tags):

        if len(tags) == 0:
            info = "没有找到对应\"" + tag_name + "\"的定义。"
            FwManager.instance().request_service("dialog.msg.warn", {'message':info})

        else:
            cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
            FwManager.instance().request_service('view.search_taglist.show_taglist', {'taglist':tags, 'project':cur_prj})
            if len(tags) == 1:
                ''' 直接跳转。 '''
                tag = tags[0]
                self._goto_file_line(tag.tag_file_path, tag.tag_line_no)
                
    def _find_reference_by_dialog(self):
        ''' 查找定义 '''
        response, tag_name = UtilDialog.show_dialog_one_entry("查找引用", '名字')
        if response != Gtk.ResponseType.OK or tag_name is None or tag_name == '':
            return

        self._search_reference(tag_name)

    def _find_reference(self):
        ''' 查找引用
        '''
        tag_name = UtilEditor.get_selected_text_or_word()
        if tag_name is None:
            self._find_reference_by_dialog()
        else:
            self._search_reference(tag_name)
            
    def _search_reference(self, tag_name):
        cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
        ModelTask.execute(self._after_search_reference,
                          cur_prj.query_reference_tags, tag_name)

    def _after_search_reference(self, tag_name, tags):
        if len(tags) == 0:
            info = "没有找到对应\"" + tag_name + "\"的引用。"
            FwManager.instance().request_service("dialog.msg.warn", {'message':info})
        else:
            cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
            FwManager.instance().request_service('view.search_taglist.show_taglist', {'taglist':tags, 'project':cur_prj})
            if len(tags) == 1:
                # 直接跳转。
                tag = tags[0]
                self._goto_file_line(tag.tag_file_path, tag.tag_line_no)

    def _go_back_tag(self):
        # 回退到上一个位置。
        # 恢复到原来的位置
        isOK, results = FwManager.instance().request_service('model.jump_history.pop')
        if results is None:
            return
        self._goto_file_line(results['file_path'], results['line_no'], record=False)

    def _update_tags_of_project(self):
        ''' 更新当前项目的TAGS，并且更新文件列表。
        TODO: 以后应该改成监听“事件”
        '''

        cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
        if cur_prj is None:
            return

        # 更新当前项目的文件列表
        FwManager.instance().request_service('view.fstree.set_dir', {'dir':cur_prj.src_dirs[0]})

        # 更新右边的TAGS
        cur_prj.prepare()

    def _add_bookmark(self):
        ''' 【服务】根据当前情况加入新的bookmark。
        '''
        bookmark = UtilEditor.make_bookmark()
        cur_prj = FwManager.request_one('project', 'view.main.get_current_project')
        cur_prj.add_bookmark(bookmark)
        return True, {'bookmarks':cur_prj.bookmarks, 'current_project': cur_prj}

    def _editor_set_focus(self):
        ''' 获取焦点(延迟调用) '''
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self._idle_editor_set_focus)

    def _idle_editor_set_focus(self):
        ''' 获取焦点 '''
        editor = FwManager.request_one('editor', "view.multi_editors.get_current_editor")
        editor.grab_focus()
