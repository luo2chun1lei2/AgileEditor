# -*- coding:utf-8 -*-
'''
和编辑器相关的共通函数！
目前不是组件！
'''

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
