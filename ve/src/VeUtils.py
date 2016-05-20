#-*- coding:utf-8 -*-

# 各种方便的工具。

import os, logging, threading

def is_empty(string):
    # 判断是否空字符串，如果是空格之类的，也是empty。
    # return:Bool:True,空 False,非空

    if string is None or len(string) == 0:
        return True
    elif string.isspace():
        return True
    else:
        return False
    
def is_not_empty(string):
    # 判断是否空字符串。
    # return:Bool:true,非空 false,空
    
    return not is_empty(string)
