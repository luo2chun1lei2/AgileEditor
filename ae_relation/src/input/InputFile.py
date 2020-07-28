# -*- coding:utf-8 -*-

# Input是所有Input的基类
# 汇集所有的输入，比如Console、文本等。
# 读取文件中的每一行处理，如果行末有“\"，那么就将此行之下合并为此行。
# 1. 以行为基本单位。但并不是说，一行就一定处理结果。文本后面不包括"\n"。

import logging
from .Input import *

class InputFile(Input):
    # 从文件中读取输入。
    def __init__(self, file_path):
        super(InputFile, self).__init__()
        self.file = open(file_path, "r")
        self.line_no = 0
        
    def open(self, path):
        self.file = open(path, "r")
        
    def read_line(self, wait=True):
        # 读取一行输入。
        # @param wait boolean 如果需要等待，就会等待输入后才返回。
        #                    如果不需要等待，就会立刻返回，返回的是None。
        #                    有些方法是必须等待的。
        # @return String 一样输入，也可能是“”。没有等到就是None。
        
        # 读取文件中的每一行处理，如果行末有“\"，那么就将此行之下合并为此行。
        
        l = self.file.readline()
        # 当达到文件结束时，会返回空字符串，不是None。如果文件中有空行，会是“\n”。
        if len(l) == 0:
            return (self.line_no, None)
        self.line_no += 1

        ll = l.replace('\n', '').strip()

        logging.debug('Execute line[%d]: %s' % (self.line_no, ll))

        return (self.line_no, ll)
