# -*- coding:utf-8 -*-

# 普通的控制台输入。

import logging, sys
from .Input import *
    
# 在内部控制或者脚本可以执行的命令。
class InputConsole(Input):
    # 从控制台获取输入。
    
    def __init__(self):
        super(InputConsole, self).__init__()
        self.line_no = 0
        
    def read_line(self, wait=True):
        sys.stdout.write(">")
        sys.stdout.flush()

        input_str = sys.stdin.readline().strip("\n")
        self.line_no = self.line_no + 1
        
        return self.line_no, input_str
