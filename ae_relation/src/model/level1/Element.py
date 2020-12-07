#-*- coding:utf-8 -*-

# 所有对象的最基础类型。

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
