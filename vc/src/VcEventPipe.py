#-*- coding:utf-8 -*-

'''
消息管道。
所有的事件都发到这里，
然后调用注册的方法。
'''

from collections import OrderedDict

class VcEventPipe:
    
    '''
    events {event_name, [call_back]}
    '''
    
    #######################################################
    ## 命令执行发出的事件
    
    EVENT_CMD_START = "cmd_start"
    # vc_cmd:VcCmd:命令
    
    EVENT_CMD_PROCESS = "cmd_process"
    # vc_cmd:VcCmd:命令 process:int:进度（0～100）
    
    EVENT_CMD_FINISH = "cmd_finish"
    # vc_cmd:VcCmd:命令 is_ok:bool result:int:错误
    
    EVENT_CMD_GRP_CANCEL = "cmd_grp_cancel"
    # 命令组执行取消。
    
    EVENT_CMD_GRP_FINISH = "cmd_grp_finish"
    # 命令组执行完成。vc_cmd_grp:VcCmdGroup
    
    EVENT_CMD_OUTPUT = "cmd_output"
    # 命令执行时，如果接收到命令就输出。vc_cmd_grp:VcGmdGroup, vc_cmd:VcCmd, text:string
    
    #######################################################
    ## 画面处理的事件
    
    # 日志说明：
    # 执行输出： -> VcCmd接受，并将日志保存在临时文件中。
    #    命令的新日志开始：此命令的日志需要清除。
    #    命令追加日志：此命令的日志添加新的内容。
    # VcCmd：-> 发送给全局
    # 画面日志知道：对应哪个任务组，已经是显示最新的，还是需要显示某个特定的日志
    #    特定日志：切换到这个状态时，显示命令的所有日志。接收到对应命令的日志后，就追加。
    #    最新日志：切换到这个状态时，显示最后执行的命令的日志，如果接到对应命令组的日志后，就追加。
    
    EVENT_LOG_COMMAND_START = "clean_log"
    # 新命令开始执行。vc_cmd:VcCmd
    
    EVENT_LOG_APPEND_TEXT = "append_log"
    # 添加日志。vc_cmd:VcCmd，text:string
    
    EVENT_LOG_SET = "set_log"
    # 显示特定日志。vc_cmd:VcCmd
    
    EVENT_LOG_LATEST = "show_latest_log"
    # 显示最新的日志。vc_cmd_grp:VcCmdGroup
    
    my_instance = None
    # 内部静态实例
    
    @staticmethod
    def instance():
        '''
        单例模式。
        '''
        if VcEventPipe.my_instance is None:
            VcEventPipe.my_instance = VcEventPipe()
            
        return VcEventPipe.my_instance
    
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
        ep = VcEventPipe.instance()
        ep._register_event_call_back(event_name, call_back)

    @staticmethod
    def unregister_event(event_name, call_back):
        ep = VcEventPipe.instance()
        ep._unregister_event_call_back(event_name, call_back)

    @staticmethod
    def send_event(event_name, *args):
        ep = VcEventPipe.instance()
        ep._send_event(event_name, *args)
