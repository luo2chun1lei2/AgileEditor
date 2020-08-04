# -*- coding:utf-8 -*-

# 应用程序层：
# 建立基本的 “parserInteractiveCommand、executorApp、model” processor。
# App相当于一个Executor/Control。
# Interactive Mode = Interview.

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
    
    def do(self, argv):
        self.processorApp.process(argv)

    def init_parser_container(self, model_name):
        
        #TODO: 怎么选择不同的output？以及model之外的模块？
        self.output = OutputGraphviz() #OutputUML()
        # TODO: model name应该用来建在model。
        self.model = ModelBasic() #UMLModel()
        
        # 用于分析“交互模式”下的命令输入。
        #self.parserInteractiveCommand = ParserInteractiveCommand(self.model)
        self.parserInteractiveCommand = ParserBasic(self.model)

    def _execute_script(self, script_path):
        # 执行一个脚本文件。
        # script_path : string: path of script file
        # return : bool: True, OK, False, failed.
        try:
            logging.debug('Open script "%s", and execute it.' % script_path)
            input = InputFile(script_path)
        
            # TODO: 这里的设计不是很好，需要再想一想。
            executor1 = ExecutorProcessor(None)
            executor = ExecutorList(executor1,
                                    #ExecutorModelUML(self.model, self.output))
                                    ExecutorModelBasic(self.model, self.output))
            processor = ProcessorBasic("script", input,
                                            self.parserInteractiveCommand,
                                            executor, self.model, self.output)
            executor1.processor = processor
            
            processor.process()

        except Exception, ex:
            # 主要是捕获文件打不开的错误。
            print ex.message
            traceback.print_exc()
            return False
        return True

    def _enter_interview(self):
        
        input = InputPrompt()
        
        executor1 = ExecutorProcessor(None)
        executor = ExecutorList(executor1,
                                    ExecutorModelUML(self.model, self.output))
        
        processorInteractive = ProcessorBasic("interview", input,
                                                   self.parserInteractiveCommand,
                                                   executor, self.model, self.output)
        
        executor1.processor = processorInteractive
        processorInteractive.process()
        # 这里退出后，app就自然退出。以后可能建立更加复杂的机制。     
