#!/usr/bin/env python
#-*- coding:utf-8 -*-

''' 和零游戏。
'''

import os, sys, getopt

from VgMain import * 

#######################################
## 窗口和主函数

def help():
    print 'vg 使用:'
    print '-h, --help: 显示帮助信息。'

def main(argv):
    ''' 分析命令参数 '''
    
    # 分析参数。
    try:
        opts, args = getopt.getopt(argv[1:], 'h', [''])
    except getopt.GetoptError, err:
        print str(err)
        help()
        sys.exit(1)
        
    for opt, a in opts:
        if opt in ('-h', '--help'):
            '显示帮助信息'
            help()
            sys.exit(0)
        else:
            print 'unknown arguments.'
            help()
            sys.exit(2)
    
    # 进入主管理模块
    vx_main = VgMain.get_instance()
    vx_main.start()

if __name__ == '__main__':
    '''  主入口  '''
    main(sys.argv)
