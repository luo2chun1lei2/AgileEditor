#-*- coding:utf-8 -*-

#######################################
# 消息管道。
# 整个程序分成两个大部分，一个是画面显示，一个是数据模型部分。
# 当数据发生了改变后，应该通知画面更新，而画面接收各种事件后，改变模型。
# 所有的事件都发到这里，然后调用注册的方法。
# 实际上，建立了整体的一个MVC结构，而不是分割成小块，每个小块之中建立MVC结构。

import logging
from collections import OrderedDict

class VeEventPipe:
    # events {event_name, [call_back]}

    EVENT_WANT_ADD_NEW_PROJECT = "want-add-new-project"
    EVENT_WANT_DEL_PROJECT = "want-del-old-project"
    EVENT_WANT_CHANGE_PROJECT = "want-change-old-project"
    
    ve_event_pipe = None
    # 静态单实例
    
    @staticmethod
    def instance():
        # 单例模式。

        # 如果没有生成，就生成。
        if VeEventPipe.ve_event_pipe is None:
            VeEventPipe.ve_event_pipe = VeEventPipe()
            
        return VeEventPipe.ve_event_pipe
    
    def __init__(self):
        self.events = OrderedDict()
    
    ###################################
    ## 给外部用的注册方法。
    
    @staticmethod
    def register_event_call_back(event_name, call_back):
        # 注册此事件的call back方法。
        # event_name:string:事件名字
        # call_function:function:call back函数
        # return:Nothing
        
        ep = VeEventPipe.instance()
        ep._register_event_call_back(event_name, call_back)

    @staticmethod
    def unregister_event_call_back(event_name, call_back):
        # 反注册
        # return:Nothing 即使错误也不返回错误
        ep = VeEventPipe.instance()
        ep._unregister_event_call_back(event_name, call_back)

    @staticmethod
    def send_event(event_name, *args):
        # 向执行事件中发送信号
        # event_name:string:事件名字
        # *args:任意长度参数：需要传递的参数
        # return: Nothing
        ep = VeEventPipe.instance()
        ep._send_event(event_name, *args)

    @staticmethod
    def want_add_new_project(prj_name, prj_src_dirs):
        # 发送“想添加项目的信息”
        # prj_name:string:项目名字
        # prj_src_dirs:[string]:项目的代码目录数组
        # return:Nothing
        VeEventPipe.send_event(VeEventPipe.EVENT_WANT_ADD_NEW_PROJECT, prj_name, prj_src_dirs)
        
    @staticmethod
    def want_del_project(prj):
        # 发送“想删除项目”的信号
        # prj:ModelProject:想删除的项目
        # return:Nothing
        VeEventPipe.send_event(VeEventPipe.EVENT_WANT_DEL_PROJECT, prj)
        
    @staticmethod
    def want_change_project(prj, prj_name, prj_src_dirs):
        # 发送“想修改项目”
        # prj:ModelProject:项目原来的信息（为了查找原来的项目）
        # prj_name:string:新的项目名字
        # prj_src_dirs:[string]:项目新的代码目录数组
        # return:Nothing
        VeEventPipe.send_event(VeEventPipe.EVENT_WANT_CHANGE_PROJECT, prj, prj_name, prj_src_dirs)
        
    ###################################
    ## 内部方法。
    def _send_event(self, event_name, *args):
        if not event_name in self.events:
            return
        
        for cb in self.events[event_name]:
            cb(*args)
    
    def _register_event_call_back(self, event_name, call_back):
        events = None
        if event_name in self.events:
            events = self.events[event_name]
        else:
            events = []
            self.events[event_name] = events
            
        if call_back in events:
            return
        else:
            events.append(call_back)
        
    def _unregister_event_call_back(self, event_name, call_back):

        if not event_name in self.events:
            logging.error("event %s is NOT existed." % (event_name))
            return
        
        events = self.events[event_name]
            
        if not call_back in events:
            logging.error("The event %s don't have this call back function." % event_name)
            return
        
        events.remove(call_back)
        