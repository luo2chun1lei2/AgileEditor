#-*- coding:utf-8 -*-

'''
消息管道。
所有的事件都发到这里，
然后调用注册的方法。
'''

from collections import OrderedDict

class VeEventPipe:
    
    '''
    events {event_name, [call_back]}
    '''

    EVENT_WANT_ADD_NEW_PROJECT = "want-add-new-project"
    EVENT_WANT_DEL_PROJECT = "want-del-old-project"
    EVENT_WANT_CHANGE_PROJECT = "want-change-old-project"
    
    # 内部静态实例
    ve_event_pipe = None
    
    @staticmethod
    def instance():
        '''
        单例模式。
        '''
        if VeEventPipe.ve_event_pipe is None:
            VeEventPipe.ve_event_pipe = VeEventPipe()
            
        return VeEventPipe.ve_event_pipe
    
    def __init__(self):
        self.events = OrderedDict()
    
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
            print "这个事件%s并不存在。" % (event_name)
            return
        
        events = self.events[event_name]
            
        if not call_back in events:
            print "这个事件%s并不存在此回调方法。" % (event_name)
            return
        
        events.remove(call_back)
        
    #------------------------------------------------------
    @staticmethod
    def register_event_call_back(event_name, call_back):
        ep = VeEventPipe.instance()
        ep._register_event_call_back(event_name, call_back)

    @staticmethod
    def unregister_event_call_back(event_name, call_back):
        ep = VeEventPipe.instance()
        ep._unregister_event_call_back(event_name, call_back)

    @staticmethod
    def send_event(event_name, *args):
        ep = VeEventPipe.instance()
        ep._send_event(event_name, *args)

    @staticmethod
    def want_add_new_project(prj_name, prj_src_dirs):
        VeEventPipe.send_event(VeEventPipe.EVENT_WANT_ADD_NEW_PROJECT, 
                       prj_name, prj_src_dirs)
        
    @staticmethod
    def want_del_project(prj):
        VeEventPipe.send_event(VeEventPipe.EVENT_WANT_DEL_PROJECT, prj)
        
    @staticmethod
    def want_change_project(prj, prj_name, prj_src_dirs):
        VeEventPipe.send_event(VeEventPipe.EVENT_WANT_CHANGE_PROJECT, prj, prj_name, prj_src_dirs)
        