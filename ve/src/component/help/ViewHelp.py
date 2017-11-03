# -*- coding:utf-8 -*-

# 对与Ide有帮助和支持的功能。

import os
from gi.repository import Gtk, Gdk, GdkPixbuf
from framework.FwBaseComponent import FwBaseComponent
#from framework.FwComponentFactory import FwComponentFactory

''' 例子
from framework.FwManager import FwManager
factory = FwManager.instance().findFactory("ViewDialogInfo")  # TODO 这个名字就在这里放着？

dialog = factory.createComponent()
dialog.show(self)
factory.destroyComponent(dialog)
'''

class VeiwDialogInfoFactory():

    fctName = "ViewDialogInfo"

    def __init__(self):
        pass

    def getName(self):
        return VeiwDialogInfoFactory.fctName

    def createComponent(self):
        return ViewDialogInfo()

    def destroyComponent(self, component):
        if component is ViewDialogInfo:
            # 因为对话框关闭时，实例也自己销毁了，所以这里不用管。
            pass

class ViewDialogInfo(FwBaseComponent, Gtk.Dialog):
    # 显示“关于”信息的对话框

    def __init__(self):
        pass

    def getName(self):
        # 只需要有一个，不需要区分名字。
        return "ViewDialogInfo"

    @staticmethod
    def show(window):

        authors = ['罗春雷']

        documentors = ['罗春雷']

        license = """
This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public License as
published by the Free Software Foundation; either version 2 of the
License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

You should have received a copy of the GNU Library General Public
License along with the Gnome Library; see the file COPYING.LIB.  If not,
write to the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""
        dirname = os.path.abspath(os.path.dirname(__file__))
        filename = os.path.join(dirname, '', '../../ve.png')
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
        transparent = pixbuf.add_alpha(True, 0xff, 0xff, 0xff)

        about = Gtk.AboutDialog(parent=window,
                                program_name='Agile Editor',
                                version='0.2',
                                copyright='(C) 2017 罗春雷',
                                license=license,
                                website='https://github.com/luo2chun1lei2/AgileEditor',
                                comments='Agile Editor.',
                                authors=authors,
                                documenters=documentors,
                                logo=transparent,
                                title='关于敏捷编辑器')

        about.connect('response', ViewDialogInfo.widget_destroy)
        about.show()

    @staticmethod
    def widget_destroy(widget, button):
        widget.destroy()

