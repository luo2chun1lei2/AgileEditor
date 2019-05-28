#-*- coding:utf-8 -*-

'''
各种工具。
'''

import uuid

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


def create_uuid():
    ''' 返回一个UUID，唯一。'''
    return uuid.uuid1()

def create_key(key1, key2):
    ''' 根据key1和key2得到唯一的Key，如果key1或者key2不同，生成的Key不同 '''
    return uuid.uuid5(key1, key2)
