# -*- coding:utf-8 -*-
'''
框架的核心处理类
'''

from framework.FwBaseComponent import FwBaseComponent
from component.help.ViewHelp import ViewDialogInfo, VeiwDialogInfoFactory
from pkg_resources import _manager

class FwManager():

    # single instance
    _manager = None

    @staticmethod
    def instance():
        if FwManager._manager is None:
            FwManager._manager = FwManager()

        return FwManager._manager

    def __init__(self):
        # {<component type name>:string, <component factory instance>:FwComponentFactory}
        # 注意这里实际上保存的是组件的类型，而不是具体的组件实例。
        self.componentFactories = {}

        self.registerFactory(VeiwDialogInfoFactory())

    def registerFactory(self, componentFactory):
        '''
        @param name: string: 工厂的名字，必须唯一
        @param componentFactory: FwComponentFactory: 工厂的实例
        '''
        self.componentFactories[componentFactory.getName()] = componentFactory

    def unregisterFactory(self, factoryName):
        '''
        @param factoryName: string: 工厂的名字
        '''
        del self.componentFactories[factoryName]

    def findFactory(self, factoryName):
        ''' 用名字查询工厂
        @param factoryName: string: 工厂的名字
        '''
        return self.componentFactories[factoryName]
