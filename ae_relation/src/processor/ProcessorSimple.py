#-*- coding:utf-8 -*-

# Processor：
# parser --> executor

from parser.ParserCommandLine import *
from model.concrete.UMLModelTest import *
from .Processor import *

class ProcessorSimple(Processor):
    # 简单的Pipe，只需要指定Parser和Executor两个。
    # 所以输入需要通过 "process()" 来输入。
    # 针对的是只需要一次性处理的情况。
    def __init__(self, mvc_name, parser, executor):
        # @param mvc_name string processor name
        super(ProcessorSimple, self).__init__(mvc_name)

        self.parserInteractiveCommand = parser
        self.executor = executor

    def process(self, input):
        #@param input Any 只要是parser可以接受的输入就可以。
        #@return None
        cmdPkgs = self.parserInteractiveCommand.parse(input)
        for cmdPkg in cmdPkgs:
            self.executor.execute(cmdPkg)