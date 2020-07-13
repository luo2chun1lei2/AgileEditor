#-*- coding:utf-8 -*-

# Parser模块：
# 1. 解析外部的传入命令。

import os, sys, getopt, logging
from parser.CommandPackage import *

class ParserCommandArgument:
    
    def show_help(self):
        # 和 PROGRAM_CMD 一致
        print 'program usage:'
        print '-h/--help: show help information.'
        print '-m/--model <name> load the given model.'
        print '-s/--script <path> run script after having loaded model.'
        print '-i/--interview start interview mode, if not, quit if run script.'
        print '--debug show log with debug level. If not, show information level.'
    
    def parse(self, argv):
        # 解析命令行的设置
        # @param argv 命令的传入参数，是字符串数组
        # @return CommandPackage[] 整理后的任务组
        
        cmdPkgs = []
    
        try:
            opts, args = getopt.getopt(argv[1:],
                                       "hm:s:i",
                                       ["help", "model=", "script=", "interview", "debug"])
        except getopt.GetoptError, err:
            print str(err)
            self.show_help()
            sys.exit(1)
        
        opt_model_name = None
        opt_script_path = None
        opt_interview_mode = False
        opt_log_debug = False
        opt_help = False
        opt_help_error = False
        
        for o, a in opts:
            if o in ('-h', '--help'):
                opt_help = True
                opt_help_error = False
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
            cmdPkg = CommandPackage(CommandId.SHOW_HELP)
            cmdPkg.error = opt_help_error
            cmdPkgs.append(cmdPkg)
        
        # set model name
        if opt_model_name:
            cmdPkg = CommandPackage(CommandId.MODEL_NAME)
            cmdPkg.model_name = opt_model_name
            cmdPkgs.append(cmdPkg)

        # execute script
        if opt_script_path:
            cmdPkg = CommandPackage(CommandId.EXECUTE_SCRIPT)
            cmdPkg.script_path = opt_script_path
            cmdPkgs.append(cmdPkg)
        
        # enter interview mode.
        if opt_interview_mode:
            cmdPkg = CommandPackage(CommandId.ENTER_INTERVIEW)
            cmdPkgs.append(cmdPkg)
        
        return cmdPkgs
 