# -*- coding:utf-8 -*-

# 通用对话框

from gi.repository import Gtk, Gdk
from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ViewDialogCommon(FwComponent):
    # 通用的对话框
    # 可以显示一个Entry或者两个Entry的对话框，然后得到输入的结果。

    def __init__(self):
        super(ViewDialogCommon, self).__init__()

    # from FwBaseComponnet
    def onRegistered(self, manager):
        info = [{'name':'dialog.common.one_entry', 'help':'show command dialog with one entry and options.'},
                {'name':'dialog.common.two_entry', 'help':'show command dialog with two entry and options.'},
                ]
        manager.register_service(info, self)

        return True

    def _get_window(self, params):
        window = None
        if 'transient_for' in params:
            window = params['transient_for']
        if window is None:
            window = FwManager.request_one('window', 'view.main.get_window')
        return window

    # from FwBaseComponnet
    def onRequested(self, manager, serviceName, params):

        options = None
        if 'options' in params:
            options = params['options']

        if serviceName == "dialog.common.one_entry":
            window = self._get_window(params)
            result_options = None
            if options is None:
                response, text = ViewDialogCommon.show_one_entry(window, params['title'], params['entry_label'], options)
            else:
                response, text, result_options = ViewDialogCommon.show_one_entry(window, params['title'], params['entry_label'], options)
            return (True, {'response': response, 'text':text, 'result_options':result_options})

        elif serviceName == "dialog.common.two_entry":
            window = self._get_window(params)
            response, text1, text2 = ViewDialogCommon.show_two_entry(
                                window, params['title'],
                                params['entry1_label'], params['text1'],
                                params['entry2_label'], params['text2'], options)
            return (True, {'response': response, 'text1':text1, 'text2':text2})

        else:
            return (False, None)

    @staticmethod
    def show_one_entry(widget, dlg_title, entry_label, options=None):
        # 显示一个Entry
        # return (response:Gtk.ResponseType, text:string)

        dialog = Gtk.Dialog(title=dlg_title,
                            transient_for=widget,
                            modal=True,
                            destroy_with_parent=True)

        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                           Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.set_default_response(Gtk.ResponseType.OK)

        content_area = dialog.get_content_area()
        hbox = Gtk.HBox(spacing=8)
        hbox.set_border_width(8)
        content_area.pack_start(hbox, False, False, 0)

        # 图标
        stock = Gtk.Image(stock=Gtk.STOCK_DIALOG_QUESTION,
                          icon_size=Gtk.IconSize.DIALOG)
        hbox.pack_start(stock, False, False, 0)

        # 添加选项。
        options_row = 0
        if options is not None:
            options_row = len(options)

        # Table布局器( TODO: Gtk用Grid取代Table)
        table = Gtk.Table(n_rows=2 + options_row, n_columns=2, homogeneous=False)
        table.set_row_spacings(4)
        table.set_col_spacings(4)
        hbox.pack_start(table, True, True, 0)

        # 输入文本框的标题
        label = Gtk.Label.new_with_mnemonic(entry_label)
        table.attach_defaults(label, 0, 1, 0, 1)

        # 输入文本框
        entry1 = Gtk.Entry()
        entry1.set_activates_default(True)
        table.attach_defaults(entry1, 1, 2, 0, 1)
        label.set_mnemonic_widget(entry1)

        # 添加选项。
        options_chk = []
        if options is not None:
            row_no = 0
            for o in options:
                chk = Gtk.CheckButton.new_with_label(o['label'])
                setattr(chk, 'option_name', o['name'])
                table.attach_defaults(chk, 1, 2, row_no + 1, row_no + 2)
                options_chk.append(chk)
                row_no = row_no + 1

        hbox.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            text = entry1.get_text()
            # 收集options设定结果
            result_options = []
            for chk in options_chk:
                result_options.append({'name': getattr(chk, 'option_name'), 'value':chk.get_active()})
        else:
            text = None
            result_options = None

        dialog.destroy()

        if options is None:
            return response, text
        else:
            return response, text, result_options

    @staticmethod
    def show_two_entry(widget, dlg_title, label_title1, text1, label_title2, text2, options=None):
        # 显示两个Entry
        # return (response:Gtk.ResponseType, text1:string, text2:string)

        dialog = Gtk.Dialog(title=dlg_title,
                            transient_for=widget,
                            modal=True,
                            destroy_with_parent=True)

        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                           Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)
        dialog.set_default_response(Gtk.ResponseType.OK)

        content_area = dialog.get_content_area()
        hbox = Gtk.HBox(spacing=8)
        hbox.set_border_width(8)
        content_area.pack_start(hbox, False, False, 0)

        stock = Gtk.Image(stock=Gtk.STOCK_DIALOG_QUESTION,
                          icon_size=Gtk.IconSize.DIALOG)

        hbox.pack_start(stock, False, False, 0)

        table = Gtk.Table(n_rows=2, n_columns=2, homogeneous=False)
        table.set_row_spacings(4)
        table.set_col_spacings(4)
        hbox.pack_start(table, True, True, 0)

        # 第一组
        label = Gtk.Label.new_with_mnemonic(label_title1)
        table.attach_defaults(label, 0, 1, 0, 1)

        entry1 = Gtk.Entry()
        entry1.set_activates_default(True)
        entry1.set_text(text1)
        table.attach_defaults(entry1, 1, 2, 0, 1)
        label.set_mnemonic_widget(entry1)

        # 第二组
        label2 = Gtk.Label.new_with_mnemonic(label_title2)
        table.attach_defaults(label2, 0, 1, 1, 2)

        entry2 = Gtk.Entry()
        entry2.set_activates_default(True)
        entry2.set_text(text2)
        table.attach_defaults(entry2, 1, 2, 1, 2)
        label.set_mnemonic_widget(entry2)

        hbox.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            text1 = entry1.get_text()
            text2 = entry2.get_text()
        else:
            text1 = None
            text2 = None

        dialog.destroy()

        return response, text1, text2
