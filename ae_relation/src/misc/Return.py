# -*- coding:utf-8 -*-

u'''
通用的返回状态
后面还可以加入新的状态。
<0: 错误信息
0 : 正确
>0: 需要执行的步骤。
'''

class Return:
    OK   = 0
    QUIT = 1
    ERROR= -1