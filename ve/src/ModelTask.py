#-*- coding:utf-8 -*-

# 执行任务的模型。

import os, logging, threading

from gi.repository import GLib, Gdk

class ModelTask:
    # 需要完成的长时间任务，放在队列中执行。
    
    @staticmethod
    def _run(call_back, func, args):
        result = func(*args)
        
        # call_back必须在主线程中运行。
        if type(result) is tuple:
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, call_back, *result)
        else:
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, call_back, result)
    
    @staticmethod
    def execute(call_back, func, *args):
        # 实现自定义的命令
        # call_back:函数:完成func后调用的回调方法，它的参数是func返回值。
        # func:函数:需要在其他线程中执行的方法
        # *args:不定长参数:传递给func的。 
        
        thread = threading.Thread(target=ModelTask._run, args=(call_back, func, args))
        thread.start()
