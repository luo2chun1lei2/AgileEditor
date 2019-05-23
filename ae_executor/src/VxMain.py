#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os, sys, getopt, shutil
from gi.repository import Gtk, Gdk, GtkSource, GLib, Pango
from gi.overrides.Gtk import TextBuffer

from VxUtils import *
from ViewWindow import *

class VxMain():
    '''
    VC 主入口程序。
    '''

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
        win.set_icon_from_file(os.path.join(base_path, "main.png"))
        win.show_all()

        Gtk.main()
        sys.exit(win.quit_code)

    def quit(self, window, event):
        Gtk.main_quit()
        sys.exit(255)
