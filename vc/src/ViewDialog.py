#-*- coding:utf-8 -*-

'''
自定义个的对话框
'''

from gi.repository import Gtk, GObject

class ViewDialogNewCommandGroup:
    ''' 创建命令组
    Entry 文本框:输入命令组的名字。
    Button 查找按钮：创建
    Button Cacel按钮：取消
    '''
    @staticmethod
    def show(parent=None):
        ''' 显示对话框
        parent Widget:父窗口，可以为空
        return (Gtk.ResponseType, string):对话框返回值，以及命令组的名字
        '''
        
        dialog = Gtk.Dialog(title='新建命令组',
                            transient_for= parent,
                            modal = True,
                            destroy_with_parent = True)
        dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                           Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        content_area = dialog.get_content_area()
        hbox = Gtk.HBox(spacing=8)
        hbox.set_border_width(8)
        content_area.pack_start(hbox, False, False, 0)

        stock = Gtk.Image(stock=Gtk.STOCK_DIALOG_QUESTION,
                          icon_size=Gtk.IconSize.DIALOG)

        hbox.pack_start(stock, False, False, 0)

        table = Gtk.Table(n_rows=1, n_columns=2, homogeneous=False)
        table.set_row_spacings(4)
        table.set_col_spacings(4)
        hbox.pack_start(table, True, True, 0)
        
        # Entry 1
        label = Gtk.Label.new_with_mnemonic("名字")
        table.attach_defaults(label, 0, 1, 0, 1)
        
        local_entry1 = Gtk.Entry()
        table.attach_defaults(local_entry1, 1, 2, 0, 1)
        label.set_mnemonic_widget(local_entry1)

        hbox.show_all()

        response = dialog.run()
        name = local_entry1.get_text()
        
        dialog.destroy()

        return response, name
    
