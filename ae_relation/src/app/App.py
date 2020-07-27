# -*- coding:utf-8 -*-

# 应用程序层：
# 建立基本的 “parserInteractiveCommand、executorApp、model” processor。
# App相当于一个Executor/Control。
# Interactive Mode = Interview.

import os, sys, logging, getopt, shutil, traceback

from mvc.model.TestModel1 import *
from processor import *
from parser import *
from executor import *
from input import *
from output import *
            
class App():

    def __init__(self):
        # 为了解析应用程序启动的命令行。
        self.processorApp = ProcessorSimple("app", ParserAppOption(), ExecutorApp(self))
        
        self.app_quit = False
    
    def do(self, argv):
        self.processorApp.process(argv)
            
    def init_parser_container(self, model_name):
        # TODO: model name应该用来建在model。
        self.output = Output()
        self.model = TestModel1()
        # TODO：有两层parser！
        self.executor = ExecutorPipe(self)
        
        self.executor2 = ExecutorModel(self.model)   # TODO: 对多个Executor怎么办？
        # 用于分析“交互模式”下的命令输入。
        self.parserInteractiveCommand = ParserInteractiveCommand(self.model)
        
        # TODO: 多余？
        input = Input()
        
        self.processorCommandLine = ProcessorBasic(model_name, input,
                                                   self.parserInteractiveCommand,
                                                   self.executor, self.model, self.output)
    

    def quit(self):
        self.app_quit = True

    def _execute_script(self, script_path):
        # 执行一个脚本文件。
        # script_path : string: path of script file
        # return : bool: True, OK, False, failed.
        try:
            logging.debug('Open script "%s", and execute it.' % script_path)
            input = InputFile(script_path)
            
            # 读取文件中的每一行处理，如果行末有“\"，那么就将此行之下合并为此行。
            cmd = ""
            line_no = 0
            while True:
                line_no, cmd = input.read_line()
                if cmd is None:
                    break
                
                cmdPkgs = self.parserInteractiveCommand.parse(line_no, cmd)
                for pkg in cmdPkgs:
                    self.processorCommandLine.executor.execute(pkg)
                    self.executor2.execute(pkg)

                if self.app_quit:
                    break
                
                cmd = ""

        except Exception, ex:
            print ex.message
            traceback.print_exc()
            return False
        return True

    def _enter_interview(self):
        
        input = InputConsole()
        
        self.processorInteractive = ProcessorBasic("interview", input,
                                                   self.parserInteractiveCommand,
                                                   self.executor, self.model, self.output)
        
        while True:
            line_no, cmd = input.read_line()
            if cmd is None:
                    break

            cmdPkgs = self.parserInteractiveCommand.parse(line_no, cmd)
            for pkg in cmdPkgs:
                self.processorInteractive.executor.execute(pkg)
                self.executor2.execute(pkg)

            if self.app_quit:
                break

    def show_inner_command_help(self):
        self.processorCommandLine.parserInteractiveCommand.show_help()
