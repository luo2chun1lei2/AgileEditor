# -*- coding:utf-8 -*-
'''
跳转历史,
'''
from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ModelJumpHistory(FwComponent):
    def __init__(self):
        super(ModelJumpHistory, self).__init__()

        # 跳转的记录 = [(file_path:string, line_no:int)]
        self.jumps = []

    # override component
    def onRegistered(self, manager):
        info = [{'name':'model.jump_history.push', 'help':'push one jump info into history.'},
                {'name':'model.jump_history.pop', 'help':'pop one jump info from history.'}]
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "model.jump_history.push":
            self._push_jump()
            return (True, None)
        elif serviceName == 'model.jump_history.pop':
            return (True, self._pop_jump())
        else:
            return (False, None)

    def _push_jump(self):
        # 记录当前的位置
        editor = FwManager.request_one('editor', "view.multi_editors.get_current_editor")
        if editor is None:
            return

        ide_file = FwManager.request_one('ide_file', 'view.multi_editors.get_current_ide_file')
        if ide_file is None:
            return

        text_buffer = editor.get_buffer()
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)

        self.jumps.append((ide_file.file_path, ite.get_line() + 1))

    def _pop_jump(self):
        # 恢复到原来的位置

        editor = FwManager.request_one('editor', "view.multi_editors.get_current_editor")
        if editor is None:
            return

        if len(self.jumps) == 0:
            return

        file_path, line_no = self.jumps.pop()
        return {'file_path':file_path, 'line_no':line_no}
