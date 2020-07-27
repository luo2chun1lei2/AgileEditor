#-*- coding:utf-8 -*-

# Processor：
# input --> parser -> --> executor --> model --> output

from parser.ParserCommandLine import *
from mvc.model.TestModel1 import *
from .Processor import *

class ProcessorBasic(Processor):
    # 可以使用的Pipe，简单的一个pipe。
    # 这里只允许各个类型有一个实例。
    
    def __init__(self, name, input, parser, executor, model, output):
        # name: string: processor name
        super(ProcessorBasic, self).__init__(name)

        self.input = input
        self.parserInteractiveCommand = parser
        self.executor = executor
        self.model = model
        self.output = output
        
    def process(self):
        # 处理。
        pass
