#-*- coding:utf-8 -*-

'''
最基础的类型
'''
import os, sys
from collections import OrderedDict

from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango

class Signal:
    # 辅助发送信号的类
    
    def __init__(self):
        self.signals = OrderedDict()
    
    def send_signal(self, name, *args):
        if not name in self.signals:
            return
        
        for cb in self.signals[name]:
            cb(*args)
        
    def register_signal_callback(self, name, call_back):
        signals = None
        if name in self.signals:
            signals = self.signals[name]
        else:
            signals = []
            self.signals[name] = signals
            
        if call_back in signals:
            return
        else:
            signals.append(call_back)
        
    def unregister_sigal_call_back(self, name, call_back):

        if not name in self.signals:
            print "这个信号\"%s\"并不存在。" % (name)
            return
        
        signals = self.signals[name]
            
        if not call_back in signals:
            print "这个事件%s并不存在此回调方法。" % (name)
            return
        
        signals.remove(call_back)

class XElement(object):
    
    # 最基础的元素
    def __init__(self):
        self.linkers = []
        self.value = None
    
    def link(self, elem):
        # 当elem发生改变后，此对象也跟着变化
        self.linkers.append(elem)
        
    def unlink(self, elem):
        if elem in self.linkers:
            self.linkers.remove(elem)
            
    def bind(self, elem):
        # 双向连接，一方发生改变，就另外一方发生变化
        # TODO 以后实现可以多个对象绑定
        self.link(elem)
        elem.link(self)
        
#     def on_changed(self):
#         # 请实现当发生变化后的处理
#         pass
    
    # set/get value是一组方法，实现对于value的设定和读取。
    def set_value(self, value):
        # 请每个对象自行实现
        self.value = value
        for linker in self.linkers:
            linker.set_value(value)
        
    def get_value(self):
        # 请每个对象自行实现
        return self.value 
        
#     def _signal(self, name, args):
#         # 发送信号
#         self.send_signal(name, args)
#         
#     def _register(self, name, call_back):
#         # 注册信号
#         self.register(name, call_back)
        
class XContainer(XElement):
    # 可以包含元素列表
    
    def __init__(self):
        super(XContainer, self).__init__()
        self.container = {}
    
    def add(self, key, elem):
        self.container[key] = elem
        
    def remove(self, key, elem):
        self.container.remove(key)
        
    def get_elem(self, key):
        return self.container[key]
        
# class XApp(XElement):
#     # 应用程序
#     
#     def __init__(self):
#         pass
#     
#     def start(self):
#         # 启动
#         # TODO 是否应该变成动作？
#         pass
# 
    
class XText(XElement):
    # 文本
    def __init__(self):
        super(XText, self).__init__()
     
class XViewText(Gtk.TextView, XElement):
    # 可以显示文本的图形
    def __init__(self):
        #super(XViewText, self).__init__()
        Gtk.TextView.__init__(self)
        XElement.__init__(self)
        
        self.get_buffer().connect("changed", self._on_changed)
        
    def _on_changed(self, textbuffer):
        text = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter(), False)
        self.set_value(text)

    def set_value(self, value):
        
        super(XViewText, self).set_value(value)
        
        # 为了避免无穷调用，需要判断值是否相同
        if self.get_value() is not value:
            self.get_buffer().set_text(value)

    def get_value(self):
        textbuffer = self.get_buffer()
        text = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter(), False)
        return text
    
class XViewWindow(XContainer):
    # 总的画面，是一个容器
    def __init__(self):
        
        super(XViewWindow, self). __init__ ()
        
        # 创建窗口，并进入主循环。
        self.win = Gtk.Window(title="vz")
        
        # 多余的方法，有利于使用。 
        base_path = os.path.dirname((os.path.abspath(sys.argv[0])))
        self.win.set_icon_from_file(os.path.join(base_path, "vz.png"))
         
        # 关闭方法
        self.win.connect("delete-event", self._quit)
        
        # 加入一个缺省的容器
        self.views = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.win.add(self.views)
         
    def _quit(self, window, event):
        Gtk.main_quit()
         
    def show(self):
        self.win.set_default_size(800, 600)
        self.win.show_all()
        # TODO 是否建立app对象管理这个Gtk.main()
        Gtk.main()
        
    def add(self, key, elem):
        super(XViewWindow, self).add(key, elem)
        self.views.pack_start(elem, False, True, 2)
        