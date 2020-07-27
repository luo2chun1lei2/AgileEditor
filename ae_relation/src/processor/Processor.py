#-*- coding:utf-8 -*-

# Processor：
# input --> parserInteractiveCommand --> executorApp --> model --> output

from parser.ParserCommandLine import *
from mvc.model.TestModel1 import *

class Processor(object):
    # 负责最基本的工作和接口，建立一个处理队列
    # 1. 整合 MVC 作为一个整体。
    # 2. TODO 对外提供什么标准操作？
    def __init__(self, name):
        # 设定processor的名字，这样多个processor时，可以切换。
        # TODO: 这里需要建立全局的mvc的名字注册机制，然后才能用名字实现model的创建。
        #    这里的mvc_name不是script名字，它应该是缓存的模型数据的名字。
        # TODO: control and model 应该组装在一起。
        # name: string: 是整个process的名字，而不是model的名字，虽然可以简单的等于。
        
        self.name = name
    
    def do(self, input):
        # Pipe开始正式运行。
        pass
