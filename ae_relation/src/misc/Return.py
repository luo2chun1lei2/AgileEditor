# -*- coding:utf-8 -*-

u'''
通用的返回状态
后面还可以加入新的状态。
<0: 错误信息
0 : 正确
>0: 需要执行的步骤。
'''

class Return:
    # 不是错误，而是无法处理。
    UNKNOWN = 2
    QUIT = 1
    OK   = 0
    # 小于0的是错误，ERROR不是具体的错误信息。
    ERROR= -1
    