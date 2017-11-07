# -*- coding:utf-8 -*-
'''
组件的工厂类。
'''

from framework import FwComponent

# TODO 不准备要了！
class FwComponentFactory123():
    def __init__(self):
        pass

    def getName(self):
        ''' Factory's name，只允许有一个，所以必须
        @return string: 工厂名字
        '''
        return None

    def createComponent(self):
        ''' 创建需要的组件。
        @return FwComponent: 生成组件
        '''
        return None

    def destroyComponent(self, component):
        ''' 销毁组件 (TODO dialog之类的无法调用这个函数！)
        @param component: FwComponent: 要被销毁的组件
        '''
        pass
