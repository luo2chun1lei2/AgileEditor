#-*- coding:utf-8 -*-

# Processor：
# input --> parser -> --> executor --> mvc --> output

from parser.ParserCommandLine import *
from mvc.model.TestModel1 import *
from .Processor import *

class ProcessorBasic(Processor):
    # 可以使用的Pipe，简单的一个pipe。
    # 这里只允许各个类型有一个实例。
    
    def __init__(self, name, input, parser, executor, model, output):
        # name: string: processor name
        super(ProcessorBasic, self).__init__(name)
        
        self.my_quit = False

        self.input = input
        self.parser = parser
        self.executor = executor
        self.model = model
        self.output = output
    
    def quit(self):
        self.my_quit = True
        
    def show_help(self):
        self.parser.show_help()
    
    def process(self):
        # 处理，有可能陷入无限循环等待。

        while True:
            line_no, cmd = self.input.read_line()
            if cmd is None:
                    break
    
            cmdPkgs = self.parser.parse(line_no, cmd)
            for pkg in cmdPkgs:
                self.executor.execute(pkg)
    
            if self.my_quit:
                break
