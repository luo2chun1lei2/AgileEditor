#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
在系统中加入全局按键处理。
"""

import os, sys, gtk, getopt, keybinder, subprocess

def usage():
    print 'vs 使用:'
    print '-h, --help: 显示帮助信息。'

def start_vx():
    command = "vx"
    work_dir = os.path.expanduser("~/")
    p = subprocess.Popen(command, shell=True, executable="/bin/bash", 
                         cwd = work_dir,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
    
    # 直到命令结束。
    (stdoutdata, stderrdata) = p.communicate()
    print "end of process."
    
#     obj_result = p.poll()
#     if obj_result == 0:
#         print "is OK"
#     else:
#         print "is Error"
    
def on_start_pressed():
    ''' 启动命令。 '''
    start_vx()
    
def on_stop_pressed():
    ''' 关闭自己。'''
    gtk.main_quit()

def main(argv):
    
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
            # 目前没有用。
            workshop_dir = a
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)
    
    # 开始连接快捷键
    keybinder1 = keybinder.bind("F12",  on_start_pressed)
    keybinder2 = keybinder.bind("<Control>F12",  on_stop_pressed)
    
    gtk.main()

if __name__ == '__main__':
    '''  主入口  '''
    main(sys.argv)
    