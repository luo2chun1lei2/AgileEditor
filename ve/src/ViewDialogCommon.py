#-*- coding:utf-8 -*-

'''
通用对话框
'''

from gi.repository import Gtk, Gdk

class ViewDialogCommon:
    
    @staticmethod
    def show_one_entry(widget, dlg_title, entry_label):
        '''
        return (response:Gtk.ResponseType, text:string)
        '''
        
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
        label = Gtk.Label.new_with_mnemonic(entry_label)
        table.attach_defaults(label, 0, 1, 0, 1)
        
        entryLine = Gtk.Entry()
        entryLine.set_activates_default(True)
        table.attach_defaults(entryLine, 1, 2, 0, 1)
        label.set_mnemonic_widget(entryLine)
        
        hbox.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            text = entryLine.get_text()
        else:
            text = None

        dialog.destroy()
        
        return response, text
    
    @staticmethod
    def show_two_entry(widget, dlg_title, label_title1, label_title2):
        # return (response:Gtk.ResponseType, text:string, text:string)
        
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
        
        entryLine = Gtk.Entry()
        entryLine.set_activates_default(True)
        table.attach_defaults(entryLine, 1, 2, 0, 1)
        label.set_mnemonic_widget(entryLine)
        
        # 第二组
        label2 = Gtk.Label.new_with_mnemonic(label_title2)
        table.attach_defaults(label2, 0, 1, 1, 2)
        
        entryLine2 = Gtk.Entry()
        entryLine2.set_activates_default(True)
        table.attach_defaults(entryLine2, 1, 2, 1, 2)
        label.set_mnemonic_widget(entryLine2)
        
        hbox.show_all()

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            text1 = entryLine.get_text()
            text2 = entryLine2.get_text()
        else:
            text1 = None
            text2 = None

        dialog.destroy()
        
        return response, text1, text2