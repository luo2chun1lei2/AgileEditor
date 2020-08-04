#-*- coding:utf-8 -*-

# Element and Relation,
# 属于容器中的所有对象的最基础类型。
# 类的开头：
#   A: 普通的类(Agile的缩写)
#   Enable: 能力，相当于接口。

import os, sys, logging

from misc.GlobalName import *
from .Element import *

class Relation(Element):
    # 描述一个或多个元素之间的关系。
    # Relation也是Element的一种。
    
    def __init__(self, category, name, no):
        super(Relation, self).__init__(category, name, no)
        # TODO: Relation涉及到的Element有顺序关系吗？
        self.elements = []
        
    def attach_element(self, element):
        if element not in self.elements:
            self.elements.append(element)
            element.attach_relation(self)
            
    def detach_element(self, element):
        if element in self.elements:
            self.elements.remove(element)
            element.detach_relation(self)
            
    def list_elements(self):
        for e in self.elements:
            print e.name
