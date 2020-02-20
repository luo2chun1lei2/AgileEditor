#-*- coding:utf-8 -*-

# Parser层，Container模块：
# 1. 包含若干MVC，每个MVC都是一个独立的模块组，可以执行。

from Control import *
from mvc.model.TestModel1 import *

class Container():
    def __init__(self, mvc_name):
        # mvc_name: string: mvc name
        # 根据model 的名字，初始化整个container。
        
        # TODO: 这里需要建立全局的mvc的名字注册机制，然后才能用名字实现model的创建。
        # TODO: control and model 应该组装在一起。
        self.control = Control()
        self.model = TestModel1()
        
    
    def get_current_control(self):
        return self.control
    
    def do_action_by_current_control(self, str_action):
        return self.control.do(self.model, str_action)