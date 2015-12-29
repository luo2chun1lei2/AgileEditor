#-*- coding:utf-8 -*-

'''
消息管道。
所有的事件都发到这里，
然后调用注册的方法。
'''

from collections import OrderedDict

class VxEventPipe:
    
    '''
    events {event_name, [call_back]}
    '''
    
    EVENT_CMD_START = "cmd_start"
    # vc_cmd:VcCmd:命令
    
    EVENT_CMD_PROCESS = "cmd_process"
    # vc_cmd:VcCmd:命令 process:int:进度（0～100）
    
    EVENT_CMD_FINISH = "cmd_finish"
    # vc_cmd:VcCmd:命令 is_ok:bool result:int:错误
    
    EVENT_CMD_CANCEL = "cmd_cancel"
    # 所有的命令执行取消
    
    EVENT_CMD_OUTPUT = "command_add_output"
    # text:string
    
    EVENT_LOG_CLEAN = "clean_log"
    # 
    
    EVENT_LOG_APPEND = "append_log"
    # text:string
    
    EVENT_LOG_SET = "set_log"
    # text:string
    
    my_instance = None
    # 内部静态实例
    
    @staticmethod
    def instance():
        '''
        单例模式。
        '''
        if VxEventPipe.my_instance is None:
            VxEventPipe.my_instance = VxEventPipe()
            
        return VxEventPipe.my_instance
    
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
    def register_event(event_name, call_back):
        ep = VxEventPipe.instance()
        ep._register_event_call_back(event_name, call_back)

    @staticmethod
    def unregister_event(event_name, call_back):
        ep = VxEventPipe.instance()
        ep._unregister_event_call_back(event_name, call_back)

    @staticmethod
    def send_event(event_name, *args):
        ep = VxEventPipe.instance()
        ep._send_event(event_name, *args)
