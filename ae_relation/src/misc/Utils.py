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
    
def util_trip_quoted_name(str_name):
    start = 0
    end = len(str_name)+1
    
    if len(str_name) == 0:
        return ""
    
    if str_name[0] == '"':
        start = 1
    if str_name[-1] == '"':
        end = len(str_name)-1
        
    return str_name[start:end]
        
def util_split_command_args(str_args):
    # 将一个命令行的参数，按照空格分割成字符串
    # 1. -x "xxx xxx" ，双引号内的字符串，不应该分割
    # str: string
    # return: [string]: 分割好的段，如果数据为空，那么就返回 []。
    args = []
    str = str_args.strip()
    if len(str) == 0:
        return args
    
    # 1. 以 i 为起始点，遍历整个字符串，（上面保证str不是以空格开头和结尾的）
    # 2. 找到 i 之后的第一个空格为next，第一个“为q_next,
    # 3.1 如果 b_next > q_next，那么q_next之后再找一个”为qq_next，
    #       从qq_next找第一个空格next，然后i-next之间的字符串提取出来。
    # 3.2 如果 b_next <= q_next,然后 i-next之间的字符串提取出来。
    # 3.3 b_next 不可能= q_next。
    # 4 i = b_next+1之后的第一个非空格。然后从1开始。
    i=0
    while True:
        b_next = str.find(' ', i)
        q_next = str.find('"', i)
        if b_next == -1:
            b_next = len(str)
        elif q_next != -1 and b_next > q_next:
            qq_next = str.find('"', b_next)
            if qq_next == -1:
                print "command lost one \".:"
                return []
            b_next = str.find(' ', qq_next)
            if b_next == -1: # 在第二个双引号后面，没有空格。
                b_next = qq_next+1
                
        
        args.append(str[i: b_next])
        
        i = b_next + 1
        while i<len(str) and str[i] == ' ':
            i+=1
    
        if i >= len(str):
            break
    
    return args

import unittest

class UnitTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_util_split_command_args(self):
        self.assertEqual(util_split_command_args(""), [])
        self.assertEqual(util_split_command_args("  "), [])
        self.assertEqual(util_split_command_args("123 abc ddd"), ["123", "abc", "ddd"])
        self.assertEqual(util_split_command_args("123  abc   ddd"), ["123", "abc", "ddd"])
        #self.assertEqual(util_split_command_args("123\t\tabc\tddd"), ["123", "abc", "ddd"])
        self.assertEqual(util_split_command_args("123 a=abc --c=ddd"), ["123", "a=abc", "--c=ddd"])
        self.assertEqual(util_split_command_args("123 a=\"ab c\" --c=ddd"),
                         ["123", "a=\"ab c\"", "--c=ddd"])
        self.assertEqual(util_split_command_args("123 a=\"ab c\" --c=\"d dd\""),
                         ["123", "a=\"ab c\"", "--c=\"d dd\""])

    def test_util_trip_quoted_name(self):
        self.assertEqual(util_trip_quoted_name(""), "")
        self.assertEqual(util_trip_quoted_name("abc"), 'abc')
        self.assertEqual(util_trip_quoted_name('"abc"'), 'abc')
        
