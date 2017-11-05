# -*- coding:utf-8 -*-
'''
框架管理的组件的基础类，所有的组件都必须继承实现。
<<<<<<< HEAD
TODO 组件是否需要自己知道名字？
'''

class FwBaseComponent():
    
    def __init__(self):
        self.name = None
=======
'''

class FwBaseComponent():
    def __init__(self):
        pass
>>>>>>> 5bca6cef5ca332478c19d6fed611cb1fea116cd4

    def getName(self):
        ''' 获取组件的名字
        @return string:名字 
        '''
<<<<<<< HEAD
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
=======
        return None
>>>>>>> 5bca6cef5ca332478c19d6fed611cb1fea116cd4
