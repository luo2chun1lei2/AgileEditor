#!/usr/bin/env python
#-*- coding:utf-8 -*-

# 画面部分
# 1, 顶部是菜单和工具栏（内容都随着选中的对象而定）。
# 2, 项目浏览器
# 3, 编辑器，使用GtkSourceView。
# 4, 代码浏览工具。
# 5, 编译和调试工具。
# 6, 命令工具（可以编写任意的命令）

import os, sys, getopt

from VeMain import VeMain
from VeUtils import *

#######################################
## 窗口和主函数

def usage():
    print 've usage:'
    print '-h, --help: print help message.'
    print '-p, --project <project name>: open the project.'
    print '-f, --file <file path>: open the file.'

def main(argv):
    ''' 分析命令参数
	命令(ve=visual editor)部分
	ve -p/--project <project_name>
	ve -f/--file <file_path>
    '''
    
    print "%s,%s" % (sys._getframe().f_code.co_name, sys._getframe().f_lineno)
    
    want_open_file = None
    want_open_project_name = None
    
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
    
    if not is_empty(want_open_file):
        print 'want to open file:' + want_open_file
        
    if not is_empty(want_open_project_name):
        print 'want to open project:' + want_open_project_name

    # 进入主管理模块
    ideMain = VeMain.get_instance()
    ideMain.start(want_open_project_name, want_open_file)

if __name__ == '__main__':
    '''  主入口  '''
    main(sys.argv)
