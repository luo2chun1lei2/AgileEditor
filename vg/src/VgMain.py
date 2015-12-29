#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, getopt, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango
from gi.overrides.Gtk import TextBuffer

from VgUtils import *
from ViewWindow import *

class VgMain():
    '''
    vg 主入口程序。
    '''
    
    # 配置文件所在的地方
    DEFAULT_VC_CONFIG_PATH = '~/.vg'
    
    vg_main_instance = None
    
    @staticmethod
    def get_instance():
        if VgMain.vg_main_instance is None:
            VgMain.vg_main_instance = VgMain()
            
        return VgMain.vg_main_instance

    def __init__(self):
        pass

    def start(self):
        
        # 创建窗口，并进入主循环。
        win = ViewWindow()
        win.connect("delete-event", self.quit)
        
        win.show_all()

        Gtk.main()
        
    def quit(self, window, event):
        Gtk.main_quit()
