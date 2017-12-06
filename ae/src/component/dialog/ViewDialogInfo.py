# -*- coding:utf-8 -*-

''' 显示"程序信息"信息。
'''

import os, logging

from gi.repository import Gtk, GdkPixbuf

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ViewDialogInfo(FwComponent):
    ''' 显示“信息”对话框，主要是组件、服务、消息等信息，用于测试、调试和开发。
    '''

    def __init__(self):
        super(ViewDialogInfo, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = {'name':'dialog.info', 'help':'show application information dialog.'}
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "dialog.info":
            ViewDialogInfo._show()
            return (True, None)

        else:
            return (False, None)

    @staticmethod
    def _show():

        # 准备数据
        component_info = FwManager.instance().show_components(True)
        service_info = FwManager.instance().show_services(True)
        event_info = FwManager.instance().show_events(True)

        # 生成画面
        dialog = Gtk.Dialog(title="Information")
        dialog.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.NONE)
        dialog.set_resizable(True)
        dialog.set_size_request(800, 600)

        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)

        scrolledCtrl = Gtk.ScrolledWindow()
        scrolledCtrl.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        scrolledCtrl.set_hexpand(True)
        scrolledCtrl.set_vexpand(True)
        scrolledCtrl.add(vbox)

        content_area = dialog.get_content_area()
        content_area.pack_start(scrolledCtrl, True, True, 0)

        # components
        expander = Gtk.Expander(label='Components:')
        vbox.pack_start(expander, False, False, 0)

        tv = Gtk.TextView()
        tv.get_buffer().set_text(component_info)
        tv.set_editable(False)
        expander.add(tv)

        # services
        expander = Gtk.Expander(label='services:')
        vbox.pack_start(expander, False, False, 0)

        tv = Gtk.TextView()
        tv.get_buffer().set_text(service_info)
        tv.set_editable(False)
        expander.add(tv)

        # events
        expander = Gtk.Expander(label='events')
        vbox.pack_start(expander, False, False, 0)

        tv = Gtk.TextView()
        tv.get_buffer().set_text(event_info)
        tv.set_editable(False)
        expander.add(tv)

        # 设定事件
        dialog.connect('response', ViewDialogInfo._widget_destroy)

        # 显示
        dialog.show_all()

    @staticmethod
    def _widget_destroy(widget, button):
        widget.destroy()

