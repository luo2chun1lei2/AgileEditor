# -*- coding:utf-8 -*-
'''
跳转历史,
'''
import logging
from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ModelJumpHistory(FwComponent):
    def __init__(self):
        super(ModelJumpHistory, self).__init__()

        # 跳转的记录 = [(file_path:string, line_no:int)]
        self.jumps = []
        # 当前位置(self.jumps的索引值)，如果没有数据，就是-1。
        # prev和next移动位置，push则移动到最新的位置。
        self.cur_index = -1

    # override component
    def onRegistered(self, manager):
        info = [{'name':'model.jump_history.push', 'help':'push new one jump info into history.'},
                {'name':'model.jump_history.prev', 'help':'move jump info to previous and return info.'},
                {'name':'model.jump_history.next', 'help':'move jump info to next and renturn info.'}]
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "model.jump_history.push":
            self._push_jump()
            return (True, None)
        elif serviceName == 'model.jump_history.prev':
            return (True, self._prev_jump())
        elif serviceName == 'model.jump_history.next':
            return (True, self._next_jump())
        else:
            return (False, None)

    def _push_jump(self):
        # 清理当前位置之后的所有信息，然后将新的位置推入对立。
        editor = FwManager.request_one('editor', "view.multi_editors.get_current_editor")
        if editor is None:
            return

        ide_file = FwManager.request_one('ide_file', 'view.multi_editors.get_current_ide_file')
        if ide_file is None:
            return

        # delete the info from cur_index, and append new info to tail.
        if len(self.jumps) != 0 and self.cur_index+1 <= len(self.jumps)-1:
            del self.jumps[self.cur_index+1:]   # delete the index including the from.

        text_buffer = editor.get_buffer()
        mark = text_buffer.get_insert()
        ite = text_buffer.get_iter_at_mark(mark)
        self.jumps.append((ide_file.file_path, ite.get_line() + 1))

        self.cur_index = len(self.jumps) - 1
        logging.debug("push to index=%d" % self.cur_index)
        logging.debug(self.jumps)

    def _prev_jump(self):
        # 移动到上一个地址，然后返回信息

        editor = FwManager.request_one('editor', "view.multi_editors.get_current_editor")
        if editor is None:
            return

        if len(self.jumps) == 0 or self.cur_index == 0:
            return

        self.cur_index -= 1
        file_path, line_no = self.jumps[self.cur_index]
        logging.debug("prev to index=%d" % self.cur_index)
        
        return {'file_path':file_path, 'line_no':line_no}

    def _next_jump(self):
        # 移动到下一个地址，然后返回信息

        editor = FwManager.request_one('editor', "view.multi_editors.get_current_editor")
        if editor is None:
            return
        
        if len(self.jumps) == 0 or self.cur_index >= len(self.jumps)-1:
            return
            
        self.cur_index += 1
        file_path, line_no = self.jumps[self.cur_index]
        logging.debug("next to index=%d" % self.cur_index)
        
        return {'file_path':file_path, 'line_no':line_no}
