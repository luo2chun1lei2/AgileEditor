#-*- coding:utf-8 -*-


# Element and Relation,
# 属于容器中的所有对象的最基础类型。
# 类的开头：
#   A: 普通的类(Agile的缩写)
#   Enable: 能力，相当于接口。

import os, sys, logging, getopt

from  misc.GlobalName import *
   
class Element(EnableGlobalName):
    # 基本的元素，代表了此程序中所有的基本对象。
    # 因为Python中有Object类了，避免重名，所以这里名字是Element。
    # TODO: Element的category+name是唯一性用的，是否需要加入 title 作为显示用的？
    def __init__(self, category, name, no):
        super(Element, self).__init__(category, name)
        self.no = no
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
