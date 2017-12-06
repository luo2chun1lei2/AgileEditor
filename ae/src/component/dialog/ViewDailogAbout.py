# -*- coding:utf-8 -*-

''' 显示"关于"信息。
'''

import os, logging

from gi.repository import Gtk, GdkPixbuf

from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

class ViewDialogAbout(FwComponent):
    ''' 显示“关于”信息的对话框，内部主要是开发者、网站、版本信息等等。
    '''

    def __init__(self):
        super(ViewDialogAbout, self).__init__()

    # override component
    def onRegistered(self, manager):
        info = {'name':'dialog.about', 'help':'show application about dialog.'}
        manager.register_service(info, self)

        return True

    # override component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "dialog.about":
            ViewDialogAbout._show()
            return (True, None)

        else:
            return (False, None)

    @staticmethod
    def _show():

        authors = ['罗春雷', "luo2chun1lei2@icloud.com"]

        documentors = ["罗春雷"]

        dirname = os.path.abspath(os.path.dirname(__file__))
        filename = os.path.join(dirname, '', '../../ae.png')
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        transparent = pixbuf.add_alpha(True, 0xff, 0xff, 0xff)

        window = FwManager.request_one("window", "view.main.get_window")
        about = Gtk.AboutDialog(parent=window,
                                program_name='敏捷编辑器：Agile Editor',
                                version='0.3',
                                copyright='(C) 2017 罗春雷',
                                license_type=Gtk.License.GPL_3_0,
                                website='https://github.com/luo2chun1lei2/AgileEditor',
                                comments="This editor is used for editing c/c++ program, and source navigator.",
                                authors=authors,
                                documenters=documentors,
                                logo=transparent,
                                title='关于敏捷编辑器')
        about.set_resizable(True)  # 可以改变大小
        about.connect('response', ViewDialogAbout._widget_destroy)
        about.show()

    @staticmethod
    def _widget_destroy(widget, button):
        widget.destroy()

