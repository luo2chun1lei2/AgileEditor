#-*- coding:utf-8 -*-
'''
框架的控制的基础类
负责控制所属的子模块之间的关系。

@author: luocl
'''

from FwObject import FwObject
from FwView import FwView
from FwData import FwData
from FwProcess import FwProcess

class FwControl(FwObject):
    def __init__(self):
        pass