#!/usr/bin/env python
#-*- coding:utf-8 -*-

# 研究最新的软件编程思想

import os, sys, getopt

from VzBase import *

def test():
    # 测试程序
    
    # 建立一个数据的容器
    model = XContainer()
    
    # 初始化数据模型中的数据
    model.add("name", XText())
    model.add("password", XText())
    
    # 建立一个表现形式
    win = XViewWindow()
    vName = XViewText()
    vPassword = XViewText()
    win.add("Name", vName)
    win.add("Password", vPassword)
    
    # 然后绑定
    vName.bind(model.get_elem("name"))
    vPassword.bind(model.get_elem("name"))
    #win.bind(model)
    
    # 开始
    win.show()

#######################################
## 窗口和主函数

def usage():
    print 'vz 使用:'
    print '-h, --help: 显示帮助信息。'

def main(argv):
    ''' 分析命令参数 '''
    
    # 分析参数。
    try:
        opts, args = getopt.getopt(argv[1:], 'h', ['help'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    for o, a in opts:
        if o in ('-h', '--help'):
            '显示帮助信息'
            usage()
            sys.exit(0)
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)
    
    # 进入测试程序
    test()

if __name__ == '__main__':
    '''  主入口  '''
    main(sys.argv)
