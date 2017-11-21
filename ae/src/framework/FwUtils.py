# -*- coding:utf-8 -*-
'''
框架的工具类，属于最底层的接口。

@author: luocl
'''

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

def util_print_frame():
    ''' 打印出现错误的位置的上一个调用点，用于调试。
    '''
    import inspect

    stack = inspect.stack()
    frame = stack[2][0]
    the_class = frame.f_locals["self"].__module__
    the_line = frame.f_lineno
    the_method = frame.f_code.co_name
    print "=-> %s:%d/%s" % (str(the_class), the_line, the_method)
