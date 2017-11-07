# -*- coding:utf-8 -*-
'''
框架管理的组件的基础类，所有的组件都必须继承实现。
TODO 组件是否需要自己知道名字？
'''

class FwComponent(object):

    def __init__(self):
        pass

    def onRegistered(self, manager):
        ''' 在Framework中初始化，比如注册服务等。
           Notice: 在此之前，不得调用任何服务!
        @param manager: FwManager
        @return bool: 初始化是否成功
        '''
        return False

    def onSetup(self, manager):
        ''' 初始化时，此时大部分组件已经加载，允许向其他组件请求服务。
        '''
        return True

    def onRequested(self, manager, serviceName, params):
        ''' 当接收到服务请求时的处理。
        @return (bool, map): (成功与否，结果）
        '''
        return (False, None)

    def onTeardown(self, manager):
        ''' 组件收尾工作，和 onPrepare 相反，需要注意的是，组件有可能动态的释放。
        '''
        return True

    def onUnregistered(self, manager):
        ''' 当反注册时的处理，和 onRegistered 相反。
        '''
        return True
