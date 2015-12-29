#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, getopt, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango
from gi.overrides.Gtk import TextBuffer

from VxUtils import *
from ViewWindow import *
#from VxEventPipe import *

class VxMain():
    '''
    VC 主入口程序。
    '''
    
    # 配置文件所在的地方
    DEFAULT_VC_CONFIG_PATH = '~/.vc'
    # 指定的Workshop的路径，一个人会有多个workshop。
    DEFAULT_WORKSHOP_DIR='~/workshop'
    
    vx_main_instance = None
    
    @staticmethod
    def get_instance():
        if VxMain.vx_main_instance is None:
            VxMain.vx_main_instance = VxMain()
            
        return VxMain.vx_main_instance

    def __init__(self):
        pass

    def start(self):
        
        # 创建窗口，并进入主循环。
        win = ViewWindow()
        win.connect("delete-event", self.quit)
        
        base_path = os.path.dirname((os.path.abspath(sys.argv[0])))
        win.set_icon_from_file(os.path.join(base_path, "vx.png"))
        win.show_all()

        Gtk.main()
        
    def quit(self, window, event):
        #VxExecute.reset_state()
        Gtk.main_quit()
