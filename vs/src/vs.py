#!/usr/bin/env python
#-*- coding:utf-8 -*-

#
# 在系统中加入全局按键处理。
#

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
    
    # 没有必要等到命令结束。
    p.communicate()
    #print "end of process."
    
def on_start_pressed():
    # 启动命令。
    start_vx()
    
def on_stop_pressed():
    # 关闭自己。
    gtk.main_quit()
    
def find_same_process(name):
    # return true:found, false:NOT found
    r = os.popen('ps -ef | grep %s | grep python | grep -v grep' % (name))
    
    # 因为此时已经启动vs.py，所以有一个。
    #for l in r.readlines():
    #    print l
    count = len(r.readlines()) 
    #print "count %d" % (count)
    return count > 1

def main(argv):
    
    # 分析参数。
    try:
        opts, args = getopt.getopt(argv[1:], 'h')
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
    # 如果发现已经存在这个vs，就不再启动
    if find_same_process("vs.py"):
        print "The vs.py was executing."
        return
    
    # 连接快捷键
    keybinder1 = keybinder.bind("F12",  on_start_pressed)
    keybinder2 = keybinder.bind("<control>F12",  on_stop_pressed)
    
    gtk.main()

if __name__ == '__main__':
    #  主入口  
    main(sys.argv)
    