#!/usr/bin/env python2
# -*- coding:utf-8 -*-

#这里是python的奇怪语法和第三方工具测试用的代码处。
#无关正式代码。

import sys

def main():
    while True:
        #print ">",
        s = sys.stdin.readline().strip("\n")
        s = input ('>').strip("\n")
        print "|%s|" % s
        if s == "quit":
            break
if __name__ == '__main__':
    main()
