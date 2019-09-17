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
    # 是单例模式。
    categories = {}
    
    def __init__(self):
        super(AGlobalName, self).__init__()
    
    @staticmethod
    def check_name(category, name):
        # @param category: string: 对象所在的种类
        # @param name: string: 需要注册的名字
        # @return False:有重复的名字，True:可以注册
        if not category in AGlobalName.categories:
            return True
    
        if name in AGlobalName.categories[category]:
            return False
        
        return True
    
    @staticmethod
    def register(category, name):
        # @param name : string : 需要注册的名字
        # @return False:有重复的名字，True:注册成功。
        
        if not category in AGlobalName.categories:
            AGlobalName.categories[category] = [name]
            return True
        
        if not name in AGlobalName.categories[category]:
            AGlobalName.categories[category].append(name)
            return True

        print '\"%s:%s\" is in global names.' % (category, name)
        return False
    
    @staticmethod
    def unregister(category, name):
        # @param name:string: 需要反注册的名字
        # 不用返回情况，因为无论如何都要被删除。
        if category in AGlobalName.categories:
            if name in AGlobalName.categories[category]:
                AGlobalName.categories[category].remove(name)
                if len(AGlobalName.categories[category]) == 0:
                    del AGlobalName.categories[category]
    
class EnableGlobalName(object):
    # 继承了这个类的类，就将要求注册全局的名字。
    
    def __init__(self, category, name):
        super(EnableGlobalName, self).__init__()
        
        rlt = AGlobalName.register(category, name)
        if not rlt:
            print "Cannot create the element with category=%d, name=\"%s\"." % (category, name)
            raise ValueError("Category(%s) and Name(%s) is duplicated." % (category, name))
    
        self.category = category
        self.name = name
    
    def __del__(self):
        AGlobalName.unregister(self.category, self.name)
        

class AElement(EnableGlobalName):
    # 基本的元素，代表了此程序中所有的基本对象。
    # 因为Python中有Object类了，避免重名，所以这里名字是Element。
    def __init__(self, category, name):
        super(AElement, self).__init__(category, name)
        self.relations = []

    # TODO: Element关于Relation的操作不对公开 ?
    def attach_relation(self, relation):
        if relation not in self.relations:
            self.relations.append(relation)
            
    def detach_relation(self, relation):
        if relation in self.relations:
            self.relations.remove(relation)
            
    def list_relations(self):
        for r in self.relations:
            print r.name
    

class ARelation(AElement):
    
    def __init__(self, category, name):
        super(ARelation, self).__init__(category, name)
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
