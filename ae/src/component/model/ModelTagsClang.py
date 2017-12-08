#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
用clang分析代码，生成代码调用流程图。
* 为了使用graphviz，需要安装“python-pygraphviz”，参考网站“http://pygraphviz.github.io/”
** 例子在 “/usr/share/doc/python-pygraphviz/examples/”
** 代码在 "/usr/share/pyshared/pygraphviz"
'''
import sys, os, logging, subprocess
import tempfile  # create temp files.
import clang.cindex
import pygraphviz as pgv

def analysis_source(cursor, level=0):
    """ 分析指定的cursor内的代码，用层级显示节点之间的包含关系。
    @param cursor: Cursor: as a node
    """
    print '-' * level + '%s, %s [line=%s, col=%s]' % \
        (cursor.kind, cursor.spelling, cursor.location.line, cursor.location.column)
    # Recurse for children of this cursor
    for c in cursor.get_children():
        analysis_source(c, level + 1)

def show_nodes(cursor):

    # 生成临时文件。
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)

    # 形成节点
    graph = pgv.AGraph()

    graph.add_edge(1, 2)
    graph.add_edge(2, 3)
    graph.add_edge(1, 3)

    # 可以显示出来，或者保存成文件。
    # logging.debug(graph.string())
    # graph.write('simple.dot')  # write to simple.dot
    # B = pgv.AGraph('simple.dot')  # can create a new graph from file

    # 显示为图形
    graph.layout()  # layout with default (neato)
    graph.draw(path)  # draw png
    subprocess.call(
        'eog %s' % path,
        shell=True, executable="/bin/bash")

def find_typerefs(cursor, type_name, level):
    """ Find all references to the type named 'type_name'
    @param cursor: Cursor: as a node
    """
    print '-' * level + '%s, %s [line=%s, col=%s]' % \
        (cursor.kind, cursor.spelling, cursor.location.line, cursor.location.column)
    # cursor.kind : CursorKind: cursor的类型。
#     if cursor.kind.is_declaration():
#         if type_name in cursor.spelling:
#             print 'Declare %s [line=%s, col=%s] "%s"' % \
#                 (type_name, cursor.location.line, cursor.location.column,
#                  cursor.spelling)
#
#     if cursor.kind.is_expression():
#         if type_name in cursor.spelling:
#             print 'Reference %s [line=%s, col=%s] "%s"' % \
#                 (type_name, cursor.location.line, cursor.location.column,
#                  cursor.spelling)

    # Recurse for children of this cursor
    for c in cursor.get_children():
        find_typerefs(c, type_name, level + 1)

def main(file_path, type_name):

    # 生成核心的Index实例
    index = clang.cindex.Index.create()
    # 用Index分析代码，这里是一个文件。
    tu = index.parse(file_path, args=["-I/home/luocl/myprojects/abc"])
    print 'Translation unit:', tu.spelling

    # 分析代码
    analysis_source(tu.cursor)

    show_nodes(tu.cursor)

    # 检索文件中的节点和 type_name 相关的。
    # find_typerefs(tu.cursor, type_name, 0)


if __name__ == "__main__":
    # set the level of log.
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    # Usage: call with <file_name: string: 需要分析的文件的路径> <type_name: string: 程序中具体的类型名字>
    main("/home/luocl/myprojects/AgileEditor/ae/src/test.cpp", 'my_print')
