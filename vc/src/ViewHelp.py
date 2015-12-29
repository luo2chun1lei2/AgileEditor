#-*- coding:utf-8 -*-

'''
对与Ide有帮助和支持的功能。
'''

from gi.repository import Gtk, Gdk

class ViewDialogInfo(Gtk.Dialog):
    ''' 显示“关于”信息的对话框 '''
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "信息", parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK),
                            modal = True)
        
        self.set_default_size(300, 200)
        
        info = "执行命令程序，版本0.1。\n" + \
            "目前提供建立命令组和执行里面命令的功能。"
        label= Gtk.Label(info)
        
        box = self.get_content_area()
        box.add(label)
        
        self.show_all()
