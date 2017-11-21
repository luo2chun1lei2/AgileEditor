# -*- coding:utf-8 -*-

'''
负责检索和跳转用的。
'''
from gi.repository import Gtk

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager
from component.util.UtilEditor import UtilEditor

class CtrlSearch(FwComponent):
    def __init__(self):
        super(CtrlSearch, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = [{'name':'ctrl.search.jump_to', 'help':'Jump to ? line.'},
                {'name':'ctrl.search.find', 'help':'get the selected word and focus on search textbox.'}  # This is NOT direct finding function.
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
            return

        (start, end) = buf.get_selection_bounds()

        text = buf.get_text(start, end, False)

        FwManager.instance().requestService('view.menu.set_and_jump_to_search_textbox', {'text': text})
