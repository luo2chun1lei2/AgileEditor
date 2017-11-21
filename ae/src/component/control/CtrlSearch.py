# -*- coding:utf-8 -*-

'''
负责检索和跳转用的。
'''
import logging
from gi.repository import Gtk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager
from component.util.UtilEditor import UtilEditor

class CtrlSearch(FwComponent):
    def __init__(self):
        super(CtrlSearch, self).__init__()
        self.search_setting = None

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.search.init', 'help':'initialize the search context.'},  # TODO 这里是否是一个服务，还应该是监听事件，应该仔细考虑！
                {'name':'ctrl.search.jump_to', 'help':'Jump to ? line.'},
                {'name':'ctrl.search.find', 'help':'get the selected word and focus on search textbox.'},  # This is NOT direct finding function.
                {'name':'ctrl.search.find_text', 'help':'begin to find text.'},
                {'name':'ctrl.search.find_next', 'help':'find the next matched word.'},
                {'name':'ctrl.search.find_prev', 'help':'find the previous matched word.'}
                ]
        manager.registerService(info, self)

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
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFind',
                  'title':None,
                  'accel':"<control>F",
                  'stock_id':Gtk.STOCK_FIND,
                  'service_name':'ctrl.search.find'}
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFindNext',
                  'title':'Find Next',
                  'accel':"<control>G",
                  'stock_id':None,
                  'service_name':'ctrl.search.find_next'}
        manager.requestService("view.menu.add", params)

        params = {'menu_name':'SearchMenu',
                  'menu_item_name':'SearchFindPrev',
                  'title':'Find Prev',
                  'accel':"<shift><control>G",
                  'stock_id':None,
                  'service_name':'ctrl.search.find_prev'}
        manager.requestService("view.menu.add", params)

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

        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if view_editor is None:
            return

        buf = view_editor.editor.get_buffer()

        if not buf.get_has_selection():
            text = None
        else:
            (start, end) = buf.get_selection_bounds()
            text = buf.get_text(start, end, False)

        FwManager.instance().requestService('view.menu.set_and_jump_to_search_textbox', {'text': text})

    def _find_next(self, search_text):
        '''
        如果当前编辑器中有选中的文字，则直接显示对话框。
        对话框中的文字，缺省被选中，可以被全文粘贴。
        然后查找定义。 
        search_text string 需要检索的文字
        '''
        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
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
        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
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
        view_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
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
