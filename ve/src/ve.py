#!/usr/bin/env python
#-*- coding:utf-8 -*-

#######################################
## 命令参数分析，启动程序。

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0') 

import os, sys, getopt, logging

from VeMain import VeMain
from VeUtils import *

def usage():
    # 显示使用信息
    print 've usage:'
    print '-h, --help: print help message.'
    print '-p, --project <project name>: open the project.'
    print '-f, --file <file path>: open the file.'

def main(argv):
    # 分析命令参数
    # 命令(ve=visual editor)部分
    # ve -p/--project <project_name>
    # ve -f/--file <file_path>
    
    # 设定日志的等级和格式
    logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')
    
    want_open_file = None   # 想要立即打开的文件名字
    want_open_project_name = None # 想要立即打开的项目名字
    
    try:
        opts, args = getopt.getopt(argv[1:], 'hp:f:', ['project=', 'file='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    for o, a in opts:
        if o in ('-h', '--help'):
            '显示帮助信息'
            usage()
            sys.exit(0)
        elif o in ('-f', '--file'):
            want_open_file = a
        elif o in ('-p', '--project'):
            want_open_project_name = a
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)
    
    # 进入主管理模块，传入需要的参数。
    veMain = VeMain.get_instance()
    veMain.start(want_open_project_name, want_open_file)

if __name__ == '__main__':
    # 主入口  
    main(sys.argv)
