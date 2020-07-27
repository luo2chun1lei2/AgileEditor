#-*- coding:utf-8 -*-

# Processor：
# input --> parserInteractiveCommand --> executorApp --> model --> output

from parser.ParserCommandLine import *
from mvc.model.TestModel1 import *

class Processor(object):
    # 负责最基本的工作和接口，建立一个处理队列
    # 1. 整合 MVC 作为一个整体。
    # 2. TODO 对外提供什么标准操作？
    def __init__(self, mvc_name):
        # 根据model 的名字，初始化整个container。
        # TODO: 这里需要建立全局的mvc的名字注册机制，然后才能用名字实现model的创建。
        #    这里的mvc_name不是script名字，它应该是缓存的模型数据的名字。
        # TODO: control and model 应该组装在一起。
        # mvc_name: string: 是整个mvc的名字，而不是model的名字，虽然可以简单的等于。
        
        self.model = None
        self.control = None
        self.mvc_name = mvc_name
    
    #def do_action_by_current_control(self, str_action):
    #    #return: Return:
    #    return self.control.do(str_action.strip())
    def do(self, input):
        # Pipe开始正式运行。
        pass

class ProcessorSimple(Processor):
    # 简单的Pipe，只需要指定Parser和Executor两个。
    def __init__(self, mvc_name, parser, executor):
        # @param mvc_name string processor name
        super(ProcessorSimple, self).__init__(mvc_name)

        self.parserInteractiveCommand = parser
        self.executor = executor

    def do(self, input):
        #@param input Any 只要是parser可以接受的输入就可以。
        #@return None
        cmdPkgs = self.parserInteractiveCommand.parse(input)
        for cmdPkg in cmdPkgs:
            self.executor.execute(cmdPkg)

class ProcessorBasic(Processor):
    # 可以使用的Pipe，简单的一个pipe，TODO:以后要允许有多个input和output。
    def __init__(self, mvc_name, input, parser, executor, model, output):
        # mvc_name: string: mvc name
        super(ProcessorBasic, self).__init__(mvc_name)

        self.input = input
        self.parserInteractiveCommand = parser
        self.executor = executor
        self.model = model
        self.output = output
