# -*- coding:utf-8 -*-

# Input是所有Input的基类
# 汇集所有的输入，比如Console、文本等。
# 1. 以行为基本单位。但并不是说，一行就一定处理结果。文本后面不包括"\n"。

import logging

class Input(object):
    def __init__(self):
        super(Input, self).__init__()

    def read_line(self, wait=True):
        # 读取一行输入。
        #@param wait boolean 如果需要等待，就会等待输入后才返回。
        #                    如果不需要等待，就会立刻返回，返回的是None。
        #                    有些方法是必须等待的。
        # @return (int, String) (行号，一行文字)，
        #                    行号，从1开始。文字也可能是“”。没有等到就是None。
        return (0, None)
