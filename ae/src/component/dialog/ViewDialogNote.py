# -*- coding:utf-8 -*-

''' 显示"便捷编辑本"画面。
'''

import os, logging, subprocess

from gi.repository import Gtk

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ViewDialogNote(FwComponent):
    ''' 显示“便捷编辑本”对话框，主要方便对于文本的基于脚本的处理。
    '''

    def __init__(self):
        super(ViewDialogNote, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = {'name':'dialog.note', 'help':'show dialog editing with commands.'}
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "dialog.note":
            if ViewDialogNote._show() == 0:
                return (True, {'response':Gtk.ResponseType.OK})
            else:
                return (True, {'response':Gtk.ResponseType.CANCEL})

        else:
            return (False, None)

    @staticmethod
    def _show():

        # 执行外部的命令
        command = "vx"
        work_dir = os.path.expanduser("~/")

        # 非阻塞
#         p = subprocess.Popen(command, shell=True, executable="/bin/bash",
#                               cwd=work_dir,
#                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#         p.communicate()
#         return 255

        # 阻塞操作
        rlt = subprocess.call(command, shell=True, executable="/bin/bash", cwd=work_dir)
        return rlt

    @staticmethod
    def _widget_destroy(widget, button):
        widget.destroy()
