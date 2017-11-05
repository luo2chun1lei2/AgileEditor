# -*- coding:utf-8 -*-
'''
框架管理的组件的基础类，所有的组件都必须继承实现。
TODO 组件是否需要自己知道名字？
'''

class FwBaseComponent():
    
    def __init__(self):
        self.name = None

    def getName(self):
        ''' 获取组件的名字
        @return string:名字 
        '''
        return self.name
    
    def init(self, manager):
        ''' 在Framework中初始化，比如注册服务等。
           Notice: 在此之前，不得调用任何服务!
        @param manager: FwManager
        @return bool: 初始化是否成功
        '''
        return False

    def dispatchService(self, manager, serviceName, params):
        '''
        @return (bool, map): (成功与否，结果）
        '''
        return (False, None)
