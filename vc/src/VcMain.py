#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, getopt, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango
from gi.overrides.Gtk import TextBuffer

from VcUtils import *
from ViewWindow import *
from VcEventPipe import *
from VcCmd import *

class VcMain():
    '''
    VC 主入口程序。
    '''
    
    # 配置文件所在的地方
    DEFAULT_VC_CONFIG_PATH = '~/.vc'
    # 指定的Workshop的路径，一个人会有多个workshop。
    DEFAULT_WORKSHOP_DIR='~/workshop'
    
    vc_main_instance = None
    
    @staticmethod
    def get_instance():
        if VcMain.vc_main_instance is None:
            VcMain.vc_main_instance = VcMain()
            
        return VcMain.vc_main_instance

    def __init__(self):
        # 加载工作空间。
        self.ve_path = os.path.expanduser(VcMain.DEFAULT_VC_CONFIG_PATH)
        self.workshop_dir = os.path.expanduser(VcMain.DEFAULT_WORKSHOP_DIR)

    def start(self, want_workshop_dir):
        
        if not is_empty(want_workshop_dir):
            self.workshop_dir = want_workshop_dir
        
        # 初始化一些内部的环境
        VcPlatform.instance().init(self.workshop_dir)
        
        # 创建窗口，并进入主循环。
        editorWin = ViewWindow(self.workshop_dir)
        editorWin.connect("delete-event", self.quit)
        
        # - 以全屏显示
        editorWin.maximize()
        # 设定窗口的大小。
        #editorWin.set_default_size(800, 600)
        base_path = os.path.dirname((os.path.abspath(sys.argv[0])))
        editorWin.set_icon_from_file(os.path.join(base_path, "vc.png"))
        editorWin.show_all()

        Gtk.main()
        
    def quit(self, window, event):
        VcExecute.reset_state()
        
        Gtk.main_quit()
