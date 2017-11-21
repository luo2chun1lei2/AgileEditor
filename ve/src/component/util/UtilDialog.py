# -*- coding:utf-8 -*-
'''
工具类：dialog相关的函数
'''

from framework.FwManager import FwManager

class UtilDialog:

    @staticmethod
    def show_dialog_one_entry(title, label):
        isOK, results = FwManager.instance().requestService('dialog.common.one_entry',
                                    {'title':title, 'entry_label':label})
        return results['response'], results['text']
