# -*- coding:utf-8 -*-

# 控制最基本的 Element 和 Relation

import os, sys, logging

from misc import *
from model import *

class ModelBasic(Model):
    # 内部可以容纳 Element 和 Relation。
    
    def __init__(self):
        super(ModelBasic, self).__init__()
        
    def create_element(self, cmdPkg):
        e = Element("Element", cmdPkg.name, cmdPkg.no)
        e.title = cmdPkg.title
        e.element_type = cmdPkg.type
        if self.add_element(cmdPkg.name, e):
            return Return.ERROR
        else:
            return Return.OK
        
    def create_relation(self, cmdPkg):
            
        from_e = self.find_element(cmdPkg.from_e)
        to_e = self.find_element(cmdPkg.to)
        
        if from_e is None or to_e is None:
            return False

        name = AGlobalName.get_unique_name("Relation")
        r = Relation("Relation", name, cmdPkg.no)
        
        r.relation_type = cmdPkg.type 
        r.title = cmdPkg.title
        r.attach_element(from_e)
        r.attach_element(to_e)

        if self.add_element(name, r):
            return Return.ERROR

        return Return.OK