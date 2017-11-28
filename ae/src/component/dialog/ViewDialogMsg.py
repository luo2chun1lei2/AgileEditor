# -*- coding:utf-8 -*-
'''
显示各种信息。
'''

from gi.repository import Gtk
from framework.FwComponent import FwComponent

class ViewDialogMsg(FwComponent):
    # override component
    def onRegistered(self, manager):
        info = [{'name':'dialog.msg.error', 'help':'show error message in dialog without response.'},
                {'name':'dialog.msg.info', 'help':'show information message in dialog without response.'},
                {'name':'dialog.msg.warn', 'help':'show information message in dialog without response.'},
                {'name':'dialog.msg.question', 'help':'show question message in dialog with response.'}]
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "dialog.msg.error":
            self._show_msg(None, params['message'], Gtk.MessageType.ERROR)
            return (True, None)
        if serviceName == "dialog.msg.info":
            self._show_msg(None, params['message'], Gtk.MessageType.INFO)
            return (True, None)
        if serviceName == "dialog.msg.warn":
            self._show_msg(None, params['message'], Gtk.MessageType.WARN)
            return (True, None)

        if serviceName == "dialog.msg.question":
            return (True, {"response":self._show_question(None, params['message'])})

        else:
            return (False, None)

    def _show_msg(self, window, message, message_type):
        # 显示错误消息
        dialog = Gtk.MessageDialog(transient_for=window,
                                   modal=True,
                                   destroy_with_parent=True,
                                   message_type=message_type,
                                   buttons=Gtk.ButtonsType.OK,
                                   text=message)
        dialog.run()
        dialog.destroy()

    def _show_question(self, window, message):
        dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.QUESTION, Gtk.ButtonsType.YES_NO, message)
        response = dialog.run()
        dialog.destroy()
        return response
