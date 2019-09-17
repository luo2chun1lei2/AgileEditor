#-*- coding:utf-8 -*-

u'''
    Element and Relation
类的开头：
    A: 普通的类
    Enable: 能力
'''

import os, sys, logging, getopt

class AGlobalName(object):
    
    # 管理所有元素的名字，不能有重复！
    names = []
    
    def __init__(self):
        super(AGlobalName, self).__init__()
    
    @staticmethod    
    def check_name(name):
        # @param name : string : 需要注册的名字
        # @return False:有重复的名字，True:注册成功。
        if name in AGlobalName.names:
            return False
        
        return True
    
    @staticmethod    
    def register(name):
        # @param name : string : 需要注册的名字
        # @return False:有重复的名字，True:注册成功。
        if not AGlobalName.check_name(name):
            print '\"%s\" is in global names.' % name
            return False
        
        AGlobalName.names.append(name)
        return True
    
    @staticmethod
    def unregister(name):
        # @param name:string: 需要反注册的名字
        # 不用返回情况，因为无论如何都要被删除。
        if name in AGlobalName.names:
            AGlobalName.names.remove(name)
    
class EnableGlobalName(object):
    # 继承了这个类的类，就将要求注册全局的名字。
    
    def __init__(self, name):
        super(EnableGlobalName, self).__init__()
        
        rlt = AGlobalName.register(name)
        if not rlt:
            print "Cannot create the element with name=\"%s\"." % name
            raise ValueError("Name(%s) is duplicated." % name)
    
        self.name = name
    
    def __del__(self):
        AGlobalName.unregister(self.name)
        

class AElement(EnableGlobalName):
    # 基本的元素，代表了此程序中所有的基本对象。
    # 因为Python中有Object类了，避免重名，所以这里名字是Element。
    def __init__(self, name):
        super(AElement, self).__init__(name)
        self.name = name
        

class ARelation(AElement, EnableGlobalName):
    
    def __init__(self, name):
        super(ARelation, self).__init__(name)
        self.elements = []
        
    def attach_element(self, element):
        if element not in self.elements:
            self.elements.append(element)
            
    def detach_element(self, element):
        if element in self.elements:
            self.elements.remove(element)
            
    def list_elements(self):
        for e in self.elements:
            print e.name
