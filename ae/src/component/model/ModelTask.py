# -*- coding:utf-8 -*-

''' 启动新的线程，在后台运行。完成后，会调用回调方法。
'''

import os, logging, threading

from gi.repository import GLib, Gdk, Gtk
from framework.FwManager import FwManager

class ModelTask(object):
    # 需要完成的长时间任务，放在队列中执行。

    @staticmethod
    def _run(call_back, func, args):
        # 背后执行
        # call_back:函数:结束后需要调用的方法。
        # func:函数:需要在其他线程中执行的方法
        # args:tuple:传递给func的参数元组

        result = func(*args)

        FwManager.instance().send_event('task.progress.stop')

        # call_back必须在主线程中运行。
        if type(result) is tuple:
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, call_back, *result)
        else:
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, call_back, result)

    @staticmethod
    def execute(call_back, func, *args):
        # 在其他线程执行func，结束后再调用call_back
        # call_back:函数:完成func后调用的回调方法，它的参数是func返回值。
        # func:函数:需要在其他线程中执行的方法
        # *args:不定长参数:传递给func的。

        FwManager.instance().send_event('task.progress.start')

        thread = threading.Thread(target=ModelTask._run, args=(call_back, func, args))
        thread.start()

    def __init__(self):
        super(ModelTask, self).__init__()
