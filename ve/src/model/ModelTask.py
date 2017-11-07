#-*- coding:utf-8 -*-

# 执行任务的模型。

import os, logging, threading

from gi.repository import GLib, Gdk, Gtk

class ModelTask:
    # 需要完成的长时间任务，放在队列中执行。
    
    @staticmethod
    def _run(call_back, func, args):
        # 背后执行
        # call_back:函数:结束后需要调用的方法。
        # func:函数:需要在其他线程中执行的方法
        # args:tuple:传递给func的参数元组
        
        result = func(*args)
        
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
        
        thread = threading.Thread(target=ModelTask._run, args=(call_back, func, args))
        thread.start()

    @staticmethod
    def _run_with_spinner(spinner, call_back, func, args):
        result = func(*args)
        
        if spinner:
            spinner.stop()
        
        # call_back必须在主线程中运行。
        if type(result) is tuple:
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, call_back, *result)
        else:
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, call_back, result)

    @staticmethod
    def execute_with_spinner(spinner, call_back, func, *args):
        # 在其他线程执行func，结束后再调用call_back，执行func期间，显示spinner
        # spinner:Gtk.Spinner:显示的控件。

        if spinner:
            spinner.start()
        
        thread = threading.Thread(target=ModelTask._run_with_spinner, args=(spinner, call_back, func, args))
        
        thread.start()
        