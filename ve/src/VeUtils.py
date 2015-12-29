#-*- coding:utf-8 -*-

'''
各种工具。
'''

def is_empty(string):
    ''' 判断是否空字符串。
    return true:空， false:非空。
    '''
    if string is None or len(string) == 0:
        return True
    elif string.isspace():
        return True
    else:
        return False
    
def is_not_empty(string):
    ''' 判断是否空字符串。
    return: true：非空，false:空
    '''
    return not is_empty(string)