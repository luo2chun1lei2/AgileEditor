# -*- coding:utf-8 -*-

# 应用程序层：
# 建立基本的界面，无论是 console、GUI 还是什么。
# 负责建构Parser和Container。
# 无论从 console、GUI、file还是哪里获取的执行命令（字符串），传递给Parser去执行。
# options
# -m/--model <name> 加载哪个model，缺省加载对应的control
# -s/--script <path> 加载model后，是否启动对应的
# -i/--interview 是否启动交互模式，如果没有启动交互模式，那么执行了脚本后就退出。
# --debug 显示DEBUG等级的日志
from __future__ import unicode_literals

import os, sys, logging, getopt, shutil, traceback
from Control import *
from mvc.model.TestModel1 import *

from container.Container import *
from container.Parser import *

# 用于命令提示

reload(sys)
sys.setdefaultencoding('utf8')

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter


class App():

    def __init__(self):
        self.parser = None
    
    def do(self, argv):
        self._parse_options(argv)
        
    def _show_help(self):
        # 和 PROGRAM_CMD 一致
        print 'program usage:'
        print '-h/--help: show help information.'
        print '-m/--model <name> load the given model.'
        print '-s/--script <path> run script after having loaded model.'
        print '-i/--interview start interview mode, if not, quit if run script.'
        print '--debug show log with debug level. If not, show information level.'

    def _parse_options(self, argv):
        
        u''' 解析命令行的设置 '''
    
        try:
            opts, args = getopt.getopt(argv[1:],
                                       "hm:s:i",
                                       ["help", "model=", "script=", "interview", "debug"])
        except getopt.GetoptError, err:
            print str(err)
            self._show_help()
            sys.exit(1)
        
        opt_model_name = None
        opt_script_path = None
        opt_interview_mode = False
        opt_log_debug = False
        
        for o, a in opts:
            if o in ('-h', '--help'):
                self._show_help()
                sys.exit(0)
            elif o in ('-m', '--model'):
                opt_model_name = a
            elif o in ('-s', '--script'):
                opt_script_path = a
            elif o in ('-i', '--interview'):
                opt_interview_mode = True
            elif o in ('--debug'):
                opt_log_debug = True
            else:
                print 'Find unknown option:%s' % (o) 
                self._show_help()
                sys.exit(1)
                
        # set log and level.
        if opt_log_debug:
            level = logging.DEBUG
        else:
            level = logging.INFO
        logging.basicConfig(level=level,
            format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

        # create parser and container
        container = Container(opt_model_name)
        self.parser = Parser(container)
        
        # if set script file, execute it.
        if opt_script_path:
            self._execute_script(opt_script_path)
        
        # if is interview mode, run for a loop until return quit.
        if opt_interview_mode:
            self._enter_interview()
            #is_continue = self.parser.do()

    def _execute_script(self, script_path):
        # 执行一个脚本文件。
        # script_path : string: path of script file
        # return : bool: True, OK, False, failed.
        try:
            logging.debug('Open script %s, and execute it.' % script_path)
            f = open(script_path)
            
            # 读取文件中的每一行处理，如果行末有“\"，那么就将此行之下合并为此行。
            cmd = ""
            line_no = 0
            for l in f:
                line_no += 1
                ll = l.replace('\n', '').strip()
                if len(ll) > 0 and ll[-1] == '\\':
                    cmd += ll[:-1]
                    continue
                else:
                    cmd += ll
                    
                logging.debug('Execute line[%d]: %s' % (line_no, cmd))
                rtn = self.parser.do(cmd)
                if rtn != Return.OK:
                    break
                
                cmd = ""
                    
        except Exception, ex:
            print ex.message
            traceback.print_exc()
            return False
        return True

    # 在内部控制或者脚本可以执行的命令。
    # TODO : 应该用当前Parser或者当前Control来提供
    CMDLINE_CMD = ['help', 'quit', 'test',
                    'select', 'from', 'insert', 'update', 'delete', 'drop']

    def _enter_interview(self):
        
        # 设定命令的提示符号。
        # TODO 提示的关键字，需要和下面的命令解析配套。
        word_completer = WordCompleter(App.CMDLINE_CMD, ignore_case=True)
        
        while True:
            input_str = prompt('>', completer=word_completer,
                  complete_while_typing=False)

            rtn = self.parser.do(input_str)
            if rtn == Return.QUIT:
                break
            
            
