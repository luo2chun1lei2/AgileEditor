# -*- coding:utf-8 -*-
'''
事件管理类，允许注册一个事件，然后其他的程序监听。
'''

import logging
from collections import OrderedDict

class FwListener:
    ''' 监听者
    '''
    def on_listened(self, event_name, params):
        ''' When listen one event.
        @param event_name: string: event's name
        @param params: {}: event's parameters.
        @return bool:is ok?
        '''
        return True

class FwEventPipe(object):
    ''' 消息管道，可以注册、注销和发送消息。
    '''

    def __init__(self):
        # events {event_name, [FwListener]}
        super(FwEventPipe, self).__init__()

        self.events = OrderedDict()

    ###################################
    # # 给外部用的注册方法。

#     @staticmethod
#     def register_event_call_back(event_name, call_back):
#         # 注册此事件的call back方法。
#         # event_name:string:事件名字
#         # call_function:function:call back函数
#         # return:Nothing
#
#         ep = VeEventPipe.instance()
#         self._register_event_call_back(event_name, call_back)
#
#     @staticmethod
#     def unregister_event_call_back(event_name, call_back):
#         # 反注册
#         # return:Nothing 即使错误也不返回错误
#         ep = VeEventPipe.instance()
#         ep._unregister_event_call_back(event_name, call_back)
#
#     @staticmethod
#     def send_event(event_name, *args):
#         # 向执行事件中发送信号
#         # event_name:string:事件名字
#         # *args:任意长度参数：需要传递的参数
#         # return: Nothing
#         ep = VeEventPipe.instance()
#         ep._send_event(event_name, *args)
#

    ###################################
    # 内部方法。
    def send_event(self, event_name, params=None):
        if not event_name in self.events:
            logging.debug("Nobody listen this event(%s)." % event_name)
            return True  # this is not a error.

        for listener in self.events[event_name]:
            listener.on_listened(event_name, params)

        return True

    def register_event_listener(self, event_name, listener):
        events = None
        if event_name in self.events:
            events = self.events[event_name]
        else:
            events = []
            self.events[event_name] = events

        if not listener in events:
            events.append(listener)

        return True

    def unregister_event_listerner(self, event_name, listener):

        if not event_name in self.events:
            logging.error("The event (%s) is NOT existed." % (event_name))
            return False

        events = self.events[event_name]

        if not listener in events:
            logging.error("The event (%s) has not this listener." % event_name)
            return False

        events.remove(listener)
        return True
