# -*- coding:utf-8 -*-

''' 显示帮助信息。
'''

import os, logging

from gi.repository import Gtk, GdkPixbuf

from framework.FwComponent import FwComponent
from ViewMenu import ViewMenu
from framework.FwManager import FwManager

class ViewDialogInfo(FwComponent):
    ''' 显示“关于”信息的对话框
    '''

    def __init__(self):
        pass

    # from component
    def onRegistered(self, manager):
        info = {'name':'dialog.info', 'help':'show application information dialog.'}
        manager.registerService(info, self)

        return True

    # from component
    def onSetup(self, manager):
        params = {'menu_name':'HelpMenu',
                  'menuItemName':'HelpInfo',
                  'title':"Information",
                  'accel':"<Alt>H",
                  'command_id':ViewMenu.ACTION_HELP_INFO}
        manager.requestService("view.menu.add", params)

        return True

    # from component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "dialog.info":
            ViewDialogInfo.show(None)
            return (True, None)

        else:
            return (False, None)

    @staticmethod
    def show(window):

        authors = ['罗春雷', "luo2chun1lei2@icloud.com"]

        componentInfo = FwManager.instance().showComponents(True)
        serviceInfo = FwManager.instance().showServices(True)
        documentors = ["------------------------------", componentInfo, serviceInfo]

        dirname = os.path.abspath(os.path.dirname(__file__))
        filename = os.path.join(dirname, '', '../../ve.png')
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        transparent = pixbuf.add_alpha(True, 0xff, 0xff, 0xff)

        about = Gtk.AboutDialog(parent=window,
                                program_name='Agile Editor',
                                version='0.3',
                                copyright='(C) 2017 罗春雷',
                                license_type=Gtk.License.GPL_3_0,
                                website='https://github.com/luo2chun1lei2/AgileEditor',
                                comments="This editor is used for editing c/c++ program, and source navigator.",
                                authors=authors,
                                documenters=documentors,
                                logo=transparent,
                                title='关于敏捷编辑器')

        about.connect('response', ViewDialogInfo.widget_destroy)
        about.show()

    @staticmethod
    def widget_destroy(widget, button):
        widget.destroy()

