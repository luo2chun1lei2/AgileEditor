# -*- coding:utf-8 -*-

'''
Utilities
'''

import tempfile

def util_print_frame():
    ''' 打印出现错误的位置的上一个调用点，用于调试。
    '''
    import inspect

    stack = inspect.stack()
    frame = stack[2][0]
    if "self" in frame.f_locals:
        the_class = str(frame.f_locals["self"].__module__)
    else:
        the_class = "Unknown"
    the_line = frame.f_lineno
    the_method = frame.f_code.co_name
    print "=-> %s:%d/%s" % (the_class, the_line, the_method)

class Utils(object):
    @staticmethod
    def create_tmpfile(suffix):
        # 生成临时文件。
        fd, path = tempfile.mkstemp(suffix=(".%s" % suffix))
        return fd, path
    
    @staticmethod
    def create_tmpdir():
        return tempfile.mkdtemp()