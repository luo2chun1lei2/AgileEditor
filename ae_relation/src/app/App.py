# -*- coding:utf-8 -*-

# 应用程序层：
# 建立基本的 “parser、executorApp、model” processor。
# App相当于一个Executor/Control。
# Interactive Mode = Interview.
# TODO: 下面的processor的初始化非常的奇怪，应该更加统一。

import os, sys, logging, getopt, shutil, traceback

from model.concrete.ModelUML import *
from model.concrete.ModelBasic import *
from processor import *
from parser import *
from executor import *
from input import *
from output import *
            
class App():

    def __init__(self):
        # 为了解析应用程序启动的命令行。
        self.processorApp = ProcessorSimple("app", ParserAppOption(), ExecutorApp(self))
        
        self.cur_processor_name = None
    
    def show_help(self):
        self.processorApp.show_help()
    
    def do(self, argv):
        self.processorApp.process(argv)

    def init_processor(self, processor_name):
        # 根据processor的名字，建立processor实例。
        # @param processor_name string 需要加载的processor的名字。
        # @return boolean
        
        self.cur_processor_name = processor_name
        if self.cur_processor_name == "basic":
            self.output = OutputGraphviz()
            self.model = ModelBasic()
            # 解析基本模型语言的。
            parser = ParserBasic(self.model)
        elif self.cur_processor_name == "uml":
            self.output = OutputUML()
            self.model = ModelUML()
            # 解析UML模型语言的。
            parser = ParserUML(self.model)
        else:
            logging.error("Unknown processor mode:%s" % self.cur_processor_name)
            return False
        
        # 用于分析“交互模式”下的命令输入。
        self.parser = ParserList(self.model, ParserInteractiveCommand(self.model), parser)
        
        return True

    def load_model_data(self, data_name):
        # 加载 model 的数据。 TODO: 目前还没有保存任何数据，都是用script来实现的。
        # @param data_name string data name or path.
        # @return Boolean
        return True

    def execute_script(self, script_path):
        # 执行一个脚本文件。
        # script_path : string: path of script file
        # return : bool: True, OK, False, failed.
        try:
            logging.debug('Open script "%s", and execute it.' % script_path)
            input = InputFile(script_path)
        
            # TODO: 这里的设计不是很好，需要再想一想。
            executor1 = ExecutorProcessor(None)
            if self.cur_processor_name == "basic":
                executor = ExecutorList(executor1,
                                    ExecutorModelBasic(self.model, self.output))
            elif self.cur_processor_name == "uml":
                executor = ExecutorList(executor1,
                                    ExecutorModelUML(self.model, self.output))
            processor = ProcessorBasic("script", input,
                                            self.parser,
                                            executor, self.model, self.output)
            executor1.processor = processor
            
            processor.process()

        except Exception, ex:
            # 主要是捕获文件打不开的错误。
            print ex.message
            traceback.print_exc()
            return False
        return True

    def enter_interview(self):
        # 进入到“交互”模式中，直到交互结束，才会退出这个函数。
        
        input = InputPrompt()
        
        executorProcessor = ExecutorProcessor(None)
        executorApp = ExecutorApp(self)
        if self.cur_processor_name == "basic":
            executor = ExecutorList(executorProcessor,
                                    executorApp,
                                    ExecutorModelBasic(self.model, self.output))
        elif self.cur_processor_name == "uml":
            executor = ExecutorList(executorProcessor,
                                    executorApp,
                                    ExecutorModelUML(self.model, self.output))
        
        processorInteractive = ProcessorBasic("interview", input,
                                                   self.parser,
                                                   executor, self.model, self.output)
        
        executorProcessor.processor = processorInteractive
        processorInteractive.process()
        # 这里退出后，app就自然退出。以后可能建立更加复杂的机制。     
