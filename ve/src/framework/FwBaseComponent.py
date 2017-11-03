# -*- coding:utf-8 -*-
'''
框架管理的组件的基础类，所有的组件都必须继承实现。
'''

class FwBaseComponent():
    def __init__(self):
        pass

    def getName(self):
        ''' 获取组件的名字
        @return string:名字 
        '''
        return None
