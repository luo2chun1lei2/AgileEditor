#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
利用clang分析代码，实现ModelTags模块。
目前正在实验中，距离完成还非常的遥远。
'''
import sys, os, logging, clang.cindex

def find_typerefs(node, typename):
    """ Find all references to the type named 'typename'
    """
    print '-> %s, %s [line=%s, col=%s]' % (node.kind, node.spelling, node.location.line, node.location.column)
    if node.kind.is_reference():
        if typename in node.spelling:
            print 'Found %s [line=%s, col=%s]' % (typename, node.location.line, node.location.column)
    # Recurse for children of this node
    for c in node.get_children():
        find_typerefs(c, typename)

def main(file_path, type_name):
    # main entry.

    # set the level of log.
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    index = clang.cindex.Index.create()
    tu = index.parse(file_path, args=["-I/home/luocl/myprojects/abc"])
    print 'Translation unit:', tu.spelling
    find_typerefs(tu.cursor, type_name)

if __name__ == "__main__":
    # Usage: call with <file_name: string: 需要分析的文件的路径> <type_name: string: 程序中具体的类型名字>
    main("/home/luocl/myprojects/abc/main.cpp", 'Test')
