# -*- coding:utf-8 -*-
'''
组件的工厂类。
'''

from framework import FwBaseComponent

<<<<<<< HEAD
# TODO 不准备要了！
class FwComponentFactory123():
=======
class FwComponentFactory():
>>>>>>> 5bca6cef5ca332478c19d6fed611cb1fea116cd4
    def __init__(self):
        pass

    def getName(self):
        ''' Factory's name，只允许有一个，所以必须
        @return string: 工厂名字
        '''
        return None

    def createComponent(self):
        ''' 创建需要的组件。
        @return FwBaseComponent: 生成组件
        '''
        return None

    def destroyComponent(self, component):
        ''' 销毁组件 (TODO dialog之类的无法调用这个函数！)
        @param component: FwBaseComponent: 要被销毁的组件
        '''
        pass
