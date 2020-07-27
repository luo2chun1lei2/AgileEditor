# -*- coding:utf-8 -*-

# 应用程序层：
# 建立基本的 “parserInteractiveCommand、executorApp、model” processor。
# App相当于一个Executor/Control。

import os, sys, logging, getopt, shutil, traceback
from parser.ParserCommandLine import *
from mvc.model.TestModel1 import *

from processor.Pipe import *
from parser.ParserInteractiveCommand import *
from parser.ParserAppOption import *
from executor.Executor import *
from executor.ExecutorApp import *
from executor.ExecutorPipe import *
from executor.ExecutorModel import *
from input.InputFile import *
from input.InputConsole import *
from output.Output import *
            
class App():

    def __init__(self):
        # 为了解析应用程序启动的命令行。
        self.pipeApp = ProcessorSimple("app", ParserAppOption(), ExecutorApp(self))
        
        self.app_quit = False
    
    def do(self, argv):
        self.pipeApp.do(argv)
            
    def init_parser_container(self, model_name):
        output = Output()
        model = TestModel1()
        # TODO：有两层parser！
        executor = ExecutorPipe(self) #ParserCommandLine(model)
        self.executor2 = ExecutorModel(model)   # TODO: 对多个Executor怎么办？
        # 用于分析“交互模式”下的命令输入。
        self.parserInteractiveCommand = ParserInteractiveCommand(model)
        
        # TODO: 多余？
        input = Input()
        
        self.pipe = ProcessorBasic(model_name, input, self.parserInteractiveCommand, executor, model, output)

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
                    self.pipe.executor.execute(pkg)
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
        while True:
            line_no, cmd = input.read_line()
            if cmd is None:
                    break

            cmdPkgs = self.parserInteractiveCommand.parse(line_no, cmd)
            for pkg in cmdPkgs:
                self.pipe.executor.execute(pkg)
                self.executor2.execute(pkg)

            if self.app_quit:
                break

    def show_inner_command_help(self):
        self.pipe.parserInteractiveCommand.show_help()
