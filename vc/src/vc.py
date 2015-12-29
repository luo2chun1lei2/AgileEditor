#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, getopt

from VcMain import VcMain
from VcUtils import *

#######################################
## 窗口和主函数

def usage():
    print 'vc 使用:'
    print '-h, --help: 显示帮助信息。'
    print '-d, --dir <workshop所在目录>: workshop所在的位置，如果没有，就缺省为~/workshop目录。'

def main(argv):
    ''' 分析命令参数 '''
    
    workshop_dir = None
    
    # 分析参数。
    try:
        opts, args = getopt.getopt(argv[1:], 'hd:', ['dir='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    for o, a in opts:
        if o in ('-h', '--help'):
            '显示帮助信息'
            usage()
            sys.exit(0)
        elif o in ('-d', '--dir'):
            workshop_dir = a
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)
    
    # 确保目录肯定存在。
    if is_empty(workshop_dir):
        workshop_dir = "~/workshop"
        
    workshop_dir = os.path.expanduser(workshop_dir)
    
    if not os.path.isdir(workshop_dir):
        print 'Workshop directory(%s) is NOT existed.' % (workshop_dir)
        exit(3)
    
    print 'workshop directory is ' + workshop_dir

    # 进入主管理模块
    vcMain = VcMain.get_instance()
    vcMain.start(workshop_dir)

if __name__ == '__main__':
    '''  主入口  '''
    main(sys.argv)
