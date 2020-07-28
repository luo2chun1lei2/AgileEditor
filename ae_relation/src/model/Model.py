# -*- coding:utf-8 -*-

# 模型的根类。

import os, sys, logging, getopt, shutil, traceback

from misc import *

from model.Relation import *
from model.Element import *

class Model(object):
    # 模型，所有的元素都包含在里面，这里形成一个Map，是<名字, 元素实例>。
    # TODO: id 是否都改成name？
    
    def __init__(self):
        super(Model, self).__init__()
        self.elements = {}
        
    def add_element(self, e_id, e):
        # e_id: string: element's id
        # e: object: element
        # return: bool: True, OK, False, failed.
        if e_id in self.elements:
            logging.error("Add duplicated name \"%s\" in element." % e_id)
            return False
        self.elements[e_id] = e
        
    def find_element(self, e_id):
        # e_id: string: element's id
        if not e_id in self.elements:
            logging.error("Cannot find \"%s\"" % e_id)
            return None
        return self.elements[e_id]
