# -*- coding:utf-8 -*-
'''
组件：编辑
TODO 实际上copy/cut/paste/select all 这几个动作，在GtkSource中都已经实现了，所以Menu中有，没有什么意义！
'''

from gi.repository import Gtk, GtkSource

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager
from component.util.UtilEditor import UtilEditor

class CtrlEdit(FwComponent):
    def __init__(self):
        super(CtrlEdit, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.edit.redo', 'help':'redo.'},
                {'name':'ctrl.edit.undo', 'help':'undo.'},
                {'name':'ctrl.edit.cut', 'help':'cut the selected text.'},
                {'name':'ctrl.edit.copy', 'help':'copy the selected text.'},
                {'name':'ctrl.edit.paste', 'help':'paste the text in clipboard.'},
                {'name':'ctrl.edit.comment', 'help':'make selected code to comment.'},
                {'name':'ctrl.edit.uncomment', 'help':'make selected code to uncomment.'},
                {'name':'ctrl.edit.replace', 'help':'replace the selected text by other text.'},
                {'name':'ctrl.edit.delete_line', 'help':'delete the line allocated by cursor.'},
                {'name':'ctrl.edit.select_all', 'help':'select all test in current edit file.'},
                {'name':'ctrl.edit.note', 'help':'show dialog note.'},
                ]
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "ctrl.edit.comment":
            self._edit_comment()
            return (True, None)
        elif serviceName == 'ctrl.edit.uncomment':
            self._edit_uncomment()
            return (True, None)
        elif serviceName == 'ctrl.edit.replace':
            self._edit_replace()
            return (True, None)
        elif serviceName == 'ctrl.edit.cut':
            UtilEditor.edit_cut()
            return (True, None)
        elif serviceName == 'ctrl.edit.copy':
            UtilEditor.edit_copy()
            return (True, None)
        elif serviceName == 'ctrl.edit.paste':
            UtilEditor.edit_paste()
            return (True, None)
        elif serviceName == 'ctrl.edit.delete_line':
            UtilEditor.edit_delete_line()
            return (True, None)
        elif serviceName == 'ctrl.edit.select_all':
            UtilEditor.edit_select_all()
            return (True, None)
        elif serviceName == 'ctrl.edit.redo':
            UtilEditor.edit_redo()
            return (True, None)
        elif serviceName == 'ctrl.edit.undo':
            UtilEditor.edit_undo()
            return (True, None)
        elif serviceName == 'ctrl.edit.note':
            # TODO 尝试将copy、edit、past放在一起运行，但是最后的粘贴不正确。
            FwManager.instance().request_service('ctrl.edit.copy')
            is_ok, results = FwManager.instance().request_service('dialog.note')
#             if is_ok and results['response'] == Gtk.ResponseType.OK:
#                 FwManager.instance().request_service('ctrl.edit.paste')
            return (True, None)
        else:
            return (False, None)

    # override component
    def onSetup(self, manager):
        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditRedo',
                  'title':None,
                  'accel':"<shift><control>Z",
                  'stock_id':Gtk.STOCK_REDO,
                  'service_name':'ctrl.edit.redo'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditUndo',
                  'title':None,
                  'accel':"<control>Z",
                  'stock_id':Gtk.STOCK_UNDO,
                  'service_name':'ctrl.edit.undo'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditCut',
                  'title':"Cut",
                  'accel':"",
                  'stock_id':Gtk.STOCK_CUT,
                  'service_name':'ctrl.edit.cut'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditCopy',
                  'title':"Copy",
                  'accel':"",
                  'stock_id':Gtk.STOCK_COPY,
                  'service_name':'ctrl.edit.copy'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditPaste',
                  'title':"Paste",
                  'accel':"",
                  'stock_id':Gtk.STOCK_PASTE,
                  'service_name':'ctrl.edit.paste'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditDeleteLine',
                  'title':"Delete Line",
                  'accel':"<control>D",
                  'stock_id':Gtk.STOCK_DELETE,
                  'service_name':'ctrl.edit.delete_line'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditSelectAll',
                  'title':"Select All",
                  'accel':"",
                  'stock_id':Gtk.STOCK_SELECT_ALL,
                  'service_name':'ctrl.edit.select_all'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditComment',
                  'title':"Comment",
                  'accel':"<control>slash",
                  'stock_id':None,
                  'service_name':'ctrl.edit.comment'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditUncomment',
                  'title':"Uncomment",
                  'accel':"<control>question",
                  'stock_id':None,
                  'service_name':'ctrl.edit.uncomment'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditReplace',
                  'title':"Replace",
                  'accel':"<control>R",
                  'stock_id':None,
                  'service_name':'ctrl.edit.replace'}
        manager.request_service("view.menu.add", params)

        params = {'menu_name':'EditMenu',
                  'menu_item_name':'EditNote',
                  'title':"Note",
                  'accel':"F10",
                  'stock_id':None,
                  'service_name':'ctrl.edit.note'}
        manager.request_service("view.menu.add", params)

        return True

    def _edit_comment(self):
        # 将选择的行变成“注释”
        ve_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()

        (start, end) = UtilEditor.get_selected_line(ve_editor.editor)
        if start is None or end is None:
            return

        commend_chars = UtilEditor.get_command_chars(src_buffer.get_language())
        if commend_chars is None:
            # 目前只能处理部分程序的comment。
            return

        # 在每行的开始，加入“//”，因为要修改不止一个地方，所以不能用iter。
        start_line = start.get_line()
        end_line = end.get_line()

        for line in range(start_line, end_line):
            iter_ = src_buffer.get_iter_at_line(line)
            src_buffer.insert(iter_, commend_chars)

    def _edit_uncomment(self):
        # 将所在的行从“注释“变成正常代码
        # 将选择的行变成“注释”
        ve_editor = FwManager.request_one('editor', 'view.multi_editors.get_current_ide_editor')
        if ve_editor is None:
            return

        src_buffer = ve_editor.editor.get_buffer()

        (start, end) = UtilEditor.get_selected_line(ve_editor.editor)
        if start is None or end is None:
            return

        commend_chars = UtilEditor.get_command_chars(src_buffer.get_language())
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

    def _edit_replace(self):
        # 在项目的文件中查找，不是寻找定义。

        # 看看是否已经选中了单词
        tag_name = UtilEditor.get_selected_text_or_word()

        isOK, results = FwManager.instance().request_service('dialog.common.two_entry',
                                    {'title':"替换", 'entry1_label':"从", 'text1':tag_name,
                                     'entry2_label':"到", 'text2':""})
        response = results['response']
        replace_from = results['text1']
        replace_to = results['text2']

        if response != Gtk.ResponseType.OK or replace_from is None or replace_from == '' or \
            replace_to is None or replace_to == '':
            return

        UtilEditor.replace_in_file(replace_from, replace_to)
