#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
将文本交给脚本来处理。
1, 启动后从剪贴板读取文本。
2, 然后进行处理。
3, 最后，将结果保存到剪贴板。
'''

import os, sys, getopt

from VxMain import *

#######################################
# # 窗口和主函数

def usage():
    print 'vx 使用:'
    print '-h, --help: 显示帮助信息。'

def main(argv):
    ''' 分析命令参数 '''

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
            # 没有用处。
            workshop_dir = a
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)

    # 进入主管理模块
    vx_main = VxMain.get_instance()
    vx_main.start()

if __name__ == '__main__':
    '''  主入口  '''
    main(sys.argv)
