# -*- coding:utf-8 -*-

'''
Utilities
'''

import tempfile, os

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
    #删除一个字符串前后的双引号。
    start = 0
    end = len(str_name)+1
    
    if len(str_name) == 0:
        return ""
    
    if str_name[0] == '"':
        start = 1
    if str_name[-1] == '"':
        end = len(str_name)-1
        
    return str_name[start:end]
        
def _util_find_count_in_range(s, ch, start, end):
    count = 0
    while True:
        start = s.find(ch, start, end)
        if start == -1:
            break
        count += 1
        start += 1
    return count
    
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
    # 2. 找到 i 之后的第一个空格为b_next，
    # 3. 检查 i 到 b_next 之间有多少个 ".
    # 3.1 如果有 偶数个，那么然后 i-b_next之间的字符串提取出来。
    # 3.2 如果有 奇数个，那么在 b_next之后的空格位置。跳转到2.
    i=0 # 用于copy子字符串
    start = i # 用于检索
    while True:
        b_next = str.find(' ', start)
        if b_next == -1:
            b_next = len(str)
        else:
            count = _util_find_count_in_range(str, '"', i, b_next)
            if count % 2 == 1:
                start = b_next + 1
                continue
        
        args.append(str[i: b_next])
        
        i = b_next + 1
        while i<len(str) and str[i] == ' ':
            i+=1
        if i >= len(str):
            break
        
        start = i
    
    return args

DIR_THIS_PROGRAM = None

def util_set_exe_dir(path):
    # 设置运行程序的(ae_relation)的位置
    global DIR_THIS_PROGRAM
    DIR_THIS_PROGRAM = path

def util_get_exe_dir():
    # 得到运行的程序(ae_relation)的位置
    return DIR_THIS_PROGRAM

###########################################################
## 下面是单元测试

import unittest

class UnitTestCase(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    
    def test_util_find_count_in_range(self):
        self.assertEqual(_util_find_count_in_range("", '"', 0, 0), 0)
        self.assertEqual(_util_find_count_in_range('abc', '"', 0, 3), 0)
        self.assertEqual(_util_find_count_in_range('a"b"c', '"', 0, 5), 2)
        self.assertEqual(_util_find_count_in_range('a"bc', '"', 0, 4), 1)
        self.assertEqual(_util_find_count_in_range('a"b"c', '"', 0, 3), 1)
     
    def test_util_split_command_args(self):
        self.assertEqual(util_split_command_args(""), [])
        self.assertEqual(util_split_command_args("  "), [])
        self.assertEqual(util_split_command_args("123"), ["123"])
        self.assertEqual(util_split_command_args("123 abc ddd"), ["123", "abc", "ddd"])
        self.assertEqual(util_split_command_args("123  abc   ddd"), ["123", "abc", "ddd"])
        self.assertEqual(util_split_command_args("123 a=abc --c=ddd"), ["123", "a=abc", "--c=ddd"])
        self.assertEqual(util_split_command_args("123 a=\"ab c\" --c=ddd"),
                         ["123", "a=\"ab c\"", "--c=ddd"])
        self.assertEqual(util_split_command_args("123 a=\"ab c\" --c=\"d dd\""),
                         ["123", "a=\"ab c\"", "--c=\"d dd\""])
        self.assertEqual(util_split_command_args("123 a=\"abc\" --c=\"d dd\""),
                         ["123", "a=\"abc\"", "--c=\"d dd\""])
 
    def test_util_trip_quoted_name(self):
        self.assertEqual(util_trip_quoted_name(""), "")
        self.assertEqual(util_trip_quoted_name("abc"), 'abc')
        self.assertEqual(util_trip_quoted_name('"abc"'), 'abc')
        
