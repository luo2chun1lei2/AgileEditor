#-*- coding:utf-8 -*-

# 对与Ide有帮助和支持的功能。
# TODO 目前比较简陋，以后还需要加入版本升级，和帮助功能。

from gi.repository import Gtk, Gdk

class ViewDialogInfo(Gtk.Dialog):
    # 显示“关于”信息的对话框
    
    def __init__(self, parent):
        Gtk.Dialog.__init__(self, "信息", parent, 0,
                            (Gtk.STOCK_OK, Gtk.ResponseType.OK))
        
        self.set_default_size(300, 200)
        
        info = "Workshop的集成开发环境，版本0.0.2。\n目前提供项目管理、代码编辑。"
        label= Gtk.Label(info)
        
        box = self.get_content_area()
        box.add(label)
        
        self.show_all()
