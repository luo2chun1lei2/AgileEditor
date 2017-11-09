# -*- coding:utf-8 -*-

'''
整个workshop的选项的对话框。
'''

import os, string, logging
import ConfigParser

from gi.repository import Gtk, Gdk, GtkSource

from framework.FwUtils import *
from framework.FwComponent import FwComponent
from framework.FwManager import FwManager

from model.ModelProject import ModelProject
from VeEventPipe import VeEventPipe

###########################################################

class ViewDialogWorkshopSetting(FwComponent):
    def __init__(self):
        pass

    def onRegistered(self, manager):
        info = {'name':'dialog.project.setting', 'help':'show dialog for project setting.'}
        manager.registerService(info, self)

        return True

    # from FwBaseComponnet
    def onRequested(self, manager, serviceName, params):
        if serviceName == "dialog.project.setting":
            setting = DialogPreferences.show(params['parent'], params['setting'])
            return (True, {'setting':setting})

        else:
            return (False, None)

class DialogPreferences(Gtk.Dialog):
    # 显示当前项目各种配置，并可以进行修改。

    def __init__(self, parent, setting):

        self.parent = parent
        self.setting = setting

        Gtk.Dialog.__init__(self, "Workshop设定", parent, 0,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_OK, Gtk.ResponseType.OK))

        self.set_default_size(300, 400)

        vbox = Gtk.VBox(spacing=10)

        ###############################
        # 编辑器样式(stylescheme)
        lbl_style_name = Gtk.Label("样式")
        lbl_style_name.set_justify(Gtk.Justification.LEFT)
        vbox.pack_start(lbl_style_name, False, True, 0)

        self.cmb_style = self._init_styles()
        vbox.pack_start(self.cmb_style, True, True, 0)

        ###############################
        # 字体名字
        lbl_font_name = Gtk.Label("字体")
        vbox.pack_start(lbl_font_name, True, True, 0)

        isOK, results = FwManager.instance().requestService('model.workshop.getopt', {'key':'font'})
        self.btn_font = Gtk.FontButton.new_with_font(results['value'])
        self.btn_font.connect('font-set', self.on_font_changed)
        vbox.pack_start(self.btn_font, True, True, 1.0)

        ###############################
        box = self.get_content_area()
        box.add(vbox)

        self.show_all()

    def _init_styles(self):
        styles = GtkSource.StyleSchemeManager.get_default().get_scheme_ids()

        model = Gtk.ListStore(str)
        found_index = -1
        for i in range(len(styles)):
            model.append([styles[i]])
            if styles[i] == self.setting['style']:
                found_index = i
        cmb = Gtk.ComboBox.new_with_model(model)

        cell_render = Gtk.CellRendererText.new()
        cmb.pack_start(cell_render, True)
        cmb.add_attribute(cell_render, "text", 0)
        cmb.set_active(found_index)
        cmb.connect("changed", self.on_style_changed)

        return cmb

    def on_font_changed(self, btn):
        self.setting['font'] = btn.get_font_name()
        return True

    def on_style_changed(self, combobox):
        itr = combobox.get_active_iter()
        self.setting['style'] = combobox.get_model().get_value(itr, 0)
        return True

    @staticmethod
    def show(parent, setting):
        dialog = DialogPreferences(parent, setting)

        response = dialog.run()
        if response != Gtk.ResponseType.OK:
            setting = None

        dialog.destroy()

        # 返回信息。
        return setting
