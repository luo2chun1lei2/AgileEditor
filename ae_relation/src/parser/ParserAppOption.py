#-*- coding:utf-8 -*-

import os, sys, getopt, logging

from parser.Parser import *
from parser.CommandPackage import *

class ParserAppOption(Parser):
    # 分析应用程序的命令属性的option ！
    # 1. 解析此应用外部的传入命令。
    
    def __init__(self):  #TODO: model是临时的。
        super(ParserAppOption, self).__init__()
    
    def show_help(self):
        print 'Commands for Application options:'
        print '  -h/--help : show help information.'
        print '  -p/--processor <name> : load processor, if not set use simple processor.'
        print '  -d/--data <name> : load the given model data. If not set, use empty model data.'
        print '  -s/--script <path> : run script after loading processor and model.'
        print '  -i/--interview : start interview mode, if not, quit if run script.'
        print '  -g/--debug : show log with debug level. If not, only show information level.'
    
    def parse(self, argv):
        # 解析命令行的设置
        # @param argv 命令的传入参数，是字符串数组
        # @return CommandPackage[] 整理后的任务组
        
        cmdPkgs = []
        
        try:
            opts, args = getopt.getopt(argv[1:],
                                       "hp:d:s:ig",
                                       ["help", "processor=", "data=", "script=", "interview", "debug"])
        except getopt.GetoptError, err:
            print str(err)
            self.show_help()
            sys.exit(1)
        
        opt_processor_name = None
        opt_data_name = None
        opt_script_path = None
        opt_interview_mode = False
        opt_log_debug = False
        opt_help = False
        opt_help_error = False
        
        for o, a in opts:
            if o in ('-h', '--help'):
                opt_help = True
                opt_help_error = False
            elif o in ('-p', '--processor'):
                opt_processor_name = a
            elif o in ('-d', '--data'):
                opt_data_name = a
            elif o in ('-s', '--script'):
                opt_script_path = a
            elif o in ('-i', '--interview'):
                opt_interview_mode = True
            elif o in ('-g', '--debug'):
                opt_log_debug = True
            else:
                print 'Find unknown option:%s' % (o) 
                opt_help = True
                opt_help_error = True
        
        # log  
        if opt_log_debug:
            level = logging.DEBUG
        else:
            level = logging.INFO

        cmdPkg = CommandPackage(CommandId.SET_LOG_LEVEL)
        cmdPkg.level = level
        cmdPkgs.append(cmdPkg)

        # help
        if opt_help == True:
            cmdPkg = CommandPackage(CommandId.SHOW_APP_HELP)
            cmdPkgs.append(cmdPkg)
            
            cmdPkg = CommandPackage(CommandId.QUIT)
            cmdPkg.error = opt_help_error
            cmdPkgs.append(cmdPkg)
            
        # processor, data and script 必须按照这个顺序来进行。
            
        # processor name
        if not opt_processor_name:
            opt_processor_name = "basic"
            
        cmdPkg = CommandPackage(CommandId.LOAD_PROCESSOR)
        cmdPkg.processor_name = opt_processor_name
        cmdPkgs.append(cmdPkg)
        
        # set model name
        if opt_data_name:
            cmdPkg = CommandPackage(CommandId.LOAD_DATA)
            cmdPkg.data_name = opt_data_name
            cmdPkgs.append(cmdPkg)

        # execute script
        if opt_script_path:
            cmdPkg = CommandPackage(CommandId.EXECUTE_SCRIPT)
            cmdPkg.script_path = opt_script_path
            cmdPkgs.append(cmdPkg)
        
        # enter interview mode.
        # 必须放在所有命令的后面，否则退出有问题。
        if opt_interview_mode:
            cmdPkg = CommandPackage(CommandId.ENTER_INTERVIEW)
            cmdPkgs.append(cmdPkg)
        
        return cmdPkgs
