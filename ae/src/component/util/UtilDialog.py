# -*- coding:utf-8 -*-
'''
工具类：dialog相关的函数
'''

from gi.repository import Gtk
from framework.FwManager import FwManager

class UtilDialog:

    @staticmethod
    def show_dialog_one_entry(title, label):
        isOK, results = FwManager.instance().requestService('dialog.common.one_entry',
                                    {'title':title, 'entry_label':label})
        return results['response'], results['text']

    @staticmethod
    def add_filters(dialog):
        ''' 给对话框加入过滤器 '''
        # TODO:以后应该可以打开任意文件，然后根据后缀进行判断。
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_c = Gtk.FileFilter()
        filter_c.set_name("C/Cpp/hpp files")
        filter_c.add_mime_type("text/x-c")
        dialog.add_filter(filter_c)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

#         filter_any = Gtk.FileFilter()
#         filter_any.set_name("Any files")
#         filter_any.add_pattern("*")
#         dialog.add_filter(filter_any)


