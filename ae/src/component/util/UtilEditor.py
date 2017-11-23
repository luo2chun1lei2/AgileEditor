# -*- coding:utf-8 -*-
'''
和编辑器相关的共通函数！
目前不是组件！
'''

import re, logging
from gi.repository import Gio, Gtk, Gdk, GtkSource

from framework.FwManager import FwManager

class UtilEditor(object):

    @staticmethod
    def get_selected_line(textview):
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

    @staticmethod
    def get_command_chars(language):
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

    @staticmethod
    def is_not_word(txt):
        ''' 此项目判断是否一个单词的依据。
        @param txt: string: 需要判断的文本
        @return bool: is ?
        '''
        word_pattern = re.compile("[a-zA-Z0-9_]")
        return not word_pattern.match(txt)

    @staticmethod
    def get_editor_buffer():
        ''' 获得当前的编辑器！
        '''
        editor = FwManager.requestOneSth('editor', "view.multi_editors.get_current_editor")
        if editor is None:
            return None

        return editor.get_buffer()

    @staticmethod
    def get_selected_text_or_word():
        ''' 从编辑器中得到当前被选中的文字，
        如果没有就返回光标所在的单词，
        如果都无法达到，就返回None 
        '''
        text_buf = UtilEditor.get_editor_buffer()
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
                if UtilEditor.is_not_word(txt):
                    break

                word_start.backward_char()

            # 得到以空格为区分的单词结尾。
            while True:
                n = word_end.copy()
                if not n.forward_char():
                    break
                txt = text_buf.get_text(word_end, n, False)
                if UtilEditor.is_not_word(txt):
                    break

                word_end.forward_char()

            text = text_buf.get_text(word_start, word_end, False)

        logging.debug('selected text or word is "%s"' % text)

        return text

    @staticmethod
    def make_bookmark():
        # 根据当前编辑器的当前光标位置，生成一个bookmark
        # return:ModelTag:书签

        from component.model.ModelTags import ModelTag

        text_buf = UtilEditor.get_editor_buffer()

        # 得到书签名字
        name = UtilEditor.get_selected_text_or_word()
        if name is None:
            # 就用
            name = "None"

        # 得到文件
        path = FwManager.requestOneSth('abs_file_path', 'view.multi_editors.get_current_abs_file_path')

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

    @staticmethod
    def replace_in_file(replace_from, replace_to):
        # 替换当前文件中的文字
        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
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

    @staticmethod
    def edit_cut():
        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().cut_clipboard(clipboard, True)

    @staticmethod
    def edit_copy():
        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().copy_clipboard(clipboard)

    @staticmethod
    def edit_paste():
        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        atom = Gdk.atom_intern('CLIPBOARD', True)
        clipboard = ve_editor.editor.get_clipboard(atom)
        ve_editor.editor.get_buffer().paste_clipboard(clipboard, None, True)

    @staticmethod
    def edit_select_all():
        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()
        src_buffer.select_range(src_buffer.get_start_iter(), src_buffer.get_end_iter())

    @staticmethod
    def edit_delete_line():
        # 删除光标所在的行

        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return
        src_buffer = ve_editor.editor.get_buffer()

        (start, end) = UtilEditor.get_selected_line(ve_editor.editor)
        if start is None or end is None:
            return

        src_buffer.delete(start, end)

    @staticmethod
    def edit_redo():
        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()
        if src_buffer.can_redo():
            src_buffer.redo()

    @staticmethod
    def edit_undo():
        ve_editor = FwManager.requestOneSth('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()
        if src_buffer.can_undo():
            src_buffer.undo()

    @staticmethod
    def goto_line(line_number):
        # 跳转到当前文件的行。
        # line_number:int:行号（从1开始）
        # return:Bool:False，以后不再调用，True，以后还会调用。

        if line_number < 0:
            logging.error("Error line number %d" % line_number)
            return False

        # print 'goto line number:', line_number
        text_buf = UtilEditor.get_editor_buffer()
        it = text_buf.get_iter_at_line(line_number - 1)

        text_buf.place_cursor(it)

        # 设定光标的位置，和什么都没有选中
        text_buf.select_range(it, it)
        # 屏幕滚动到这个地方。
        editor = FwManager.requestOneSth('editor', "view.multi_editors.get_current_editor")
        editor.scroll_to_iter(it, 0.25, False, 0.0, 0.5)

        # TODO:这里不是错误，而是给threads_add_idle返回不再继续调用的设定。
        return False

    @staticmethod
    def jump_to(line_number):

        # 记录当前的位置
        UtilEditor.push_jumps()

        UtilEditor.goto_line(line_number)

    @staticmethod
    def push_jumps():
        # 记录当前的位置
        FwManager.instance().requestService("model.jump_history.push")

#     @staticmethod
#     def set_src_language(src_buffer, file_path):
#         manager = GtkSource.LanguageManager()
#
#         if file_path is not None:
#             language = manager.guess_language(file_path, None)  # 设定语法的类型
#             src_buffer.set_language(language)
#         else:
#             src_buffer.set_language(None)
#
#         return src_buffer

    @staticmethod
    def set_src_language(src_buffer, file_path):

        if file_path is None:
            src_buffer.set_language(None)
            return src_buffer

        # 取出一段内容，进行判断
        f = file(file_path, 'r')
        line = f.readline()
        f.close()

        # 猜测content type，根据文件的名字
        content_type, uncertain = Gio.content_type_guess(file_path, line)
        if uncertain:
            content_type = None

        # 猜测文件的语言类型，根据文件名字的后缀
        manager = GtkSource.LanguageManager()
        language = manager.guess_language(file_path, content_type)

        src_buffer.set_language(language)  # 设定语法的类型

        return src_buffer

    @staticmethod
    def set_completion(mdl_project):
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
        completion.add_provider(mdl_project.get_completion_provider())
