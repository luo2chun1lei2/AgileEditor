# -*- coding:utf-8 -*-
'''
框架管理的组件的基础类，所有的组件都必须继承实现。
'''
from FwEvent import FwListener

from FwService import FwService

class FwComponent(object, FwListener, FwService):
    ''' 组件的基础类，每个组件都可以注册自己，以及可以监听事件，和注册自己提供的服务。
    '''

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
        注意：此方法会被反复调用，所以需要注意“重入”问题。
            另外，可能外部的组件会被替换、卸载，所以不能认为之前已经申请服务，现在不再需要。
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
