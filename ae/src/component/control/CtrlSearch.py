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

class NeedJump:
    def __init__(self, count):
        ''' count 是需要跳过的次数，因为有三个检索的控件，如果改变了其中的值，
        就会引发“changed”事件，如果三个都改变了，那么就会引发三次，所以这里是个计数器。
        '''
        self.count = count

class CtrlSearch(FwComponent):

    ACT_DEFINITION = 'def'
    ACT_REFERENCE = 'ref'
    ACT_GREP = 'grep'
    ACT_PATH = 'path'

    def __init__(self):
        super(CtrlSearch, self).__init__()
        self.search_setting = None
        self.last_search_pattern = None

        self._create_tool_item()

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.search.init', 'help':'initialize the search context.'},  # TODO 这里是否是一个服务，还应该是监听事件，应该仔细考虑！
                {'name':'ctrl.search.goto_line', 'help': 'goto the given line and focus on editor.'},
                {'name':'ctrl.search.jump_to', 'help':'Jump to ? line.'},
                {'name':'ctrl.search.focus_on_entry', 'help':'get the selected word and focus on search textbox.'},  # This is NOT direct finding function.
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
                {'name':'ctrl.search.go_forward_tag', 'help':'go forward to the next tag if exists.'},
                {'name':'ctrl.search.update_tags', 'help':'update the tags by newest project status.'},
                {'name':'ctrl.search.show_bookmark', 'help':'show a bookmark.'},
                {'name':'ctrl.search.make_bookmark', 'help': 'make one bookmark by current position, and return bookmarks list'},
                {'name':'ctrl.search_history.push', 'help': 'push one search action into one queue.'},
                {'name':'ctrl.search_history.pop', 'help': 'pop one search action from one queue.'},
                {'name':'ctrl.search_history.do_action', 'help': 'process one search action.'},
                {'name':'view.menu.set_and_jump_to_search_textbox', 'help':'jump to search textbox and set text.'},
                {'name':'view.menu.set_search_option', 'help':'set option of search.'},
                ]
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.search.jump_to":
            self._jump_to_line()
            return (True, None)
        elif serviceName == 'ctrl.search.focus_on_entry':
            self._get_word_and_jump_to_search_box()
            return (True, None)
        elif serviceName == 'ctrl.search.find_text':
            self._find_text(params['need_jump'], params['search_text'], params['need_case_sensitive'], params['need_search_is_word'])
            return (True, None)
        elif serviceName == 'ctrl.search.find_next':
            self._find_next()
            return (True, None)
        elif serviceName == 'ctrl.search.find_prev':
            self._find_prev()
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
        elif serviceName == 'ctrl.search.go_forward_tag':
            self._go_forward_tag()
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
        elif serviceName == "ctrl.search_history.push":
            FwManager.instance().request_service('model.search_history.push', params)
            return (True, None)
        elif serviceName == "ctrl.search_history.pop":
            tag = params['tag']  # ModelTag
            self._goto_file_line(tag.tag_file_path, tag.tag_line_no)
            self._editor_set_focus()
            return (True, None)
        elif serviceName == "ctrl.search_history.do_action":
            self._process_search_action(params['action_id'], params['text'])
            return (True, None)
        elif serviceName == "view.menu.set_and_jump_to_search_textbox":
            self._jump_to_search_textbox_and_set_text(params['text'])
            return (True, None)
        elif serviceName == 'view.menu.set_search_option':
            self._set_search_options(params['search_text'], params['case_sensitive'], params['is_word'])
            return (True, None)
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
                  'service_name':'ctrl.search.focus_on_entry'}
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

        # Add tool item.
        params = {'view':self.tool_item}
        manager.request_service("view.menu.add_toolbar", params)

        return True

    def _jump_to_line(self):
        from component.util.UtilDialog import UtilDialog

        # 显示一个对话框，输入需要跳转的行。
        response, text, result_options = UtilDialog.show_dialog_one_entry("跳转到行", '行')
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

    def _find_next(self):
        '''
        如果当前编辑器中有选中的文字，则直接显示对话框。
        对话框中的文字，缺省被选中，可以被全文粘贴。
        然后查找定义。 
        search_text string 需要检索的文字
        '''
        view_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if view_editor is None:
            return

        self._search_text_next(view_editor.editor.get_buffer())

    def _find_prev(self):
        '''
        如果当前编辑器中有选中的文字，则直接显示对话框。
        对话框中的文字，缺省被选中，可以被全文粘贴。
        然后查找定义。 
        search_text string 需要检索的文字
        '''
        view_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if view_editor is None:
            return

        self._search_text_prev(view_editor.editor.get_buffer())

    def _search_text_next(self, text_buffer):
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

    def _search_text_prev(self, text_buffer):
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
        result_options = None
        if pattern is None:
            options = [{'label':'单词', 'name':'is_word'}]
            response, pattern, result_options = UtilDialog.show_dialog_one_entry("在文件中检索", '模式', options)
            if response != Gtk.ResponseType.OK or pattern is None or pattern == '':
                return

            for opt in result_options:
                if opt['name'] == 'is_word' and opt['value'] == True:
                    pattern = '\\<%s\\>' % pattern

        self.last_search_pattern = pattern  # 记录最新的检索
        self._save_search_action(CtrlSearch.ACT_GREP, pattern)

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
        #if record:
        #    UtilEditor.push_jumps()

        ''' 跳转到指定文件的行。 '''
        # 先找到对应的文件，然后再滚动到指定的位置
        logging.debug('jump to path:' + file_path + ', line:' + str(line_number))
        isOK, results = FwManager.instance().request_service('ctrl.file.open', {'abs_file_path': file_path})
        if isOK and results['result'] == ViewWindow.RLT_OK:  # TODO 这里需要知道ViewWindow的常亮
            # 注意：这里采用延迟调用的方法，来调用goto_line方法，可能是buffer被设定后，
            # 还有其他的控件会通过事件来调用滚动，所以才造成马上调用滚动不成功。
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, UtilEditor.goto_line, line_number, record)

    def _find_path_with_dialog(self):
        # 检索需要的文件路径
        response, pattern, result_options = UtilDialog.show_dialog_one_entry("检索文件路径", '模式')
        if response != Gtk.ResponseType.OK or pattern is None or pattern == '':
            return

        self._save_search_action(CtrlSearch.ACT_PATH, pattern)
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
        response, tag_name, result_options = UtilDialog.show_dialog_one_entry("查找定义", '名字')
        if response != Gtk.ResponseType.OK or tag_name is None or tag_name == '':
            return

        self._save_search_action(CtrlSearch.ACT_DEFINITION, tag_name)
        self._search_definition(tag_name)

    def _find_defination(self):
        ''' 查找定义 '''
        tag_name = UtilEditor.get_selected_text_or_word()
        if tag_name is None:
            self._find_defination_by_dialog()
        else:
            self._save_search_action(CtrlSearch.ACT_DEFINITION, tag_name)
            self._search_definition(tag_name)

    def _search_definition(self, tag_name):
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
        response, tag_name, result_options = UtilDialog.show_dialog_one_entry("查找引用", '名字')
        if response != Gtk.ResponseType.OK or tag_name is None or tag_name == '':
            return

        self._save_search_action(CtrlSearch.ACT_REFERENCE, tag_name)
        self._search_reference(tag_name)

    def _find_reference(self):
        ''' 查找引用
        '''
        tag_name = UtilEditor.get_selected_text_or_word()
        if tag_name is None:
            self._find_reference_by_dialog()
        else:
            self._save_search_action(CtrlSearch.ACT_REFERENCE, tag_name)
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
        isOK, results = FwManager.instance().request_service('model.jump_history.prev')
        if results is None:
            return
        self._goto_file_line(results['file_path'], results['line_no'], record=False)

    def _go_forward_tag(self):
        # 前进到下一个位置。
        isOK, results = FwManager.instance().request_service('model.jump_history.next')
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

    def _save_search_action(self, action_id, text):
        ''' 记录检索动作。 '''
        params = {'action_id':action_id, 'text':text}
        FwManager.instance().request_service("ctrl.search_history.push", params)

    def _process_search_action(self, action_id, text):
        ''' 根据检索动作，重新检索。 '''
        if action_id == CtrlSearch.ACT_DEFINITION:
            self._search_definition(text)
        elif action_id == CtrlSearch.ACT_REFERENCE:
            self._search_reference(text)
        elif action_id == CtrlSearch.ACT_GREP:
            self._grep_in_files(text)
        elif action_id == CtrlSearch.ACT_PATH:
            self._find_path(text)

    def _create_tool_item(self):
        ''' 生成放到工具栏中的view '''

        # - 加入额外的检索Bar
        self.need_jump = NeedJump(0)

        self.search_entry = Gtk.SearchEntry()
        self.search_entry.connect("search-changed", self.on_search_options_changed, self.need_jump)

        self.search_case_sensitive = Gtk.CheckButton.new_with_label("区分大小写")
        self.search_case_sensitive.set_active(True)
        self.search_case_sensitive.connect("toggled", self.on_search_options_changed, self.need_jump)

        self.search_is_word = Gtk.CheckButton.new_with_label("单词")
        self.search_is_word.set_active(False)
        self.search_is_word.connect("toggled", self.on_search_options_changed, self.need_jump)

        hbox = Gtk.Box.new(Gtk.Orientation.HORIZONTAL, 1)
        hbox.pack_start(self.search_entry, True, True, 10)
        hbox.pack_start(self.search_case_sensitive, True, True, 2)
        hbox.pack_start(self.search_is_word, True, True, 2)

        self.tool_item = hbox

    def on_search_options_changed(self, widget, need_jump):
        search_text = self.search_entry.get_text()
        need_case_sensitive = self.search_case_sensitive.get_active()
        need_search_is_word = self.search_is_word.get_active()

        if need_jump.count == 0:
            jump = True
            logging.debug("Need Jump.")
        else:
            jump = False
        FwManager.instance().request_service('ctrl.search.find_text',
                    {'need_jump':jump, 'search_text':search_text, 'need_case_sensitive':need_case_sensitive, 'need_search_is_word':need_search_is_word})

        # TODO 不用need_jump，而是用“之前的检索选项是否相同”
        if need_jump.count > 0:
            need_jump.count -= 1

    def _jump_to_search_textbox_and_set_text(self, text):
        # 跳转到 SearchEntry中。
        # TODO 算是临时方案，首先设定为“”，然后再设定为需要的检索文字，这样就可以100%引发text_changed事件。
        if text is not None:
            self.search_entry.set_text("")
            self.search_entry.set_text(text)

        self.search_entry.grab_focus()
    def _set_search_options(self, search_text, case_sensitive, is_word):
        # 在此设置检索用的项目，想让 编辑器 显示检索项目，但是还不能跳转。下面是解决方法：（不优美）
        # 解决方法是引发事件的动作，放入一个 Object(不能是普通的数据)，然后在 on_search_options_changed 函数中，
        # 发送了信息后，再把此标志位改过来。

        self.need_jump.count = 0

        if search_text is None:
            text = ""
        else:
            text = search_text

        if text != self.search_entry.get_text():
            self.need_jump.count += 1
        if case_sensitive != self.search_case_sensitive.get_active():
            self.need_jump.count += 1
        if is_word != self.search_is_word.get_active():
            self.need_jump.count += 1

        self.search_entry.set_text(text)
        self.search_case_sensitive.set_active(case_sensitive)
        self.search_is_word.set_active(is_word)
