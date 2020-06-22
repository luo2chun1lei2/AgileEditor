#-*- coding:utf-8 -*-

# Container模块：
# 每个Container相当于一个独立的容器(VM)，这样允许一个App启动多个容器。
# 或者是复用容器的实现。
# 1. 包含若干MVC，每个MVC都是一个独立的模块组，可以执行。

from mvc.Control import *
from mvc.model.TestModel1 import *

class Container():
    # 容器的基本动作
    # 1. 整合 MVC 作为一个整体。
    # 2. TODO 对外提供什么标准操作？
    def __init__(self, mvc_name):
        # mvc_name: string: mvc name
        # 根据model 的名字，初始化整个container。
        
        # TODO: 这里需要建立全局的mvc的名字注册机制，然后才能用名字实现model的创建。
        # TODO: control and model 应该组装在一起。
        model = TestModel1()
        self.control = Control(model)
    
    def get_current_control(self):
        return self.control
    
    def do_action_by_current_control(self, str_action):
        #return: Return:
        return self.control.do(str_action.strip())