#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
用clang分析代码，生成代码调用流程图。
？？ 为什么不在 文本编辑 中直接绘制？？
* 为了使用graphviz，需要安装“python-pygraphviz”，参考网站“http://pygraphviz.github.io/”
** 例子在 “/usr/share/doc/python-pygraphviz/examples/”
** 代码在 "/usr/share/pyshared/pygraphviz"
 node's attributes: http://www.graphviz.org/doc/info/attrs.html
 label中可以加入中文，只是需要 u""。
'''
import sys, os, logging, subprocess
import tempfile  # create temp files.
import clang.cindex
import pygraphviz as pgv
from clang import cindex

class Visitor(object):
    def __init__(self):
        super(Visitor, self).__init__()

    def process(self, parent_cursor, parent_result, cursor, level):
        ''' 接受节点进行处理
        @param parent_cursor: Cursor: 父节点
        @param cursor: Cursor: 当前的节点
        @param level: int: 陷入的层次
        @return (is_continue:bool:True,继续进行，False,不再继续深入, result:object:附带结果，传给下面的节点) 。
        '''
        return True, None

    def finish(self):
        ''' 遍历节点完成 '''
        return True

class VisitorGraph(Visitor):
    def __init__(self, file_name):
        super(VisitorGraph, self).__init__()

        self.file_name = file_name

        # 生成临时文件。
        fd, self.path = tempfile.mkstemp(suffix='.png')
        os.close(fd)

        # 创建Graph
        self.graph = pgv.AGraph(directed=True)
        self.graph.graph_attr['epsilon'] = '0.001'
        # self.graph.graph_attr['rankdir'] = 'LR'  # 从左到右排列。
        # self.graph.node_attr['shape'] = 'record'  # 每个节点自定义

        self.num = 1

    # override from Visitor
    def process(self, parent_cursor, parent_result, cursor, level):
        node_no = self._add_2_graph(parent_result, cursor, level)
        return True, node_no

    # override from Visitor
    def finish(self):
        ''' 遍历节点完成 '''
        self.show()
        return True

    def _add_2_graph(self, parent_result, cursor, level):

#         if cursor.kind == cindex.CursorKind.st:
#             return False, None
        if cursor.location.file is None or self.file_name != cursor.location.file.name:
            return 0

        shape = 'record'
        if cursor.kind == cindex.CursorKind.IF_STMT:
            shape = 'triangle'

        # extent 是cursor的代码范围(SourceRange)，start和end都是SourceLocation
        # cursor.type 是语法分析后得到的节点的语法类型（比如int），如果有的话。
        e = cursor.extent
        self.graph.add_node(self.num, shape=shape, fontcolor='white', color='black', fillcolor='royalblue1', style='filled',
                            label="%s, %d:%d~%d:%d, %s" % (cursor.kind, e.start.line, e.start.column, e.end.line, e.end.column, cursor.spelling))

        # cursor.location(SourceLocation) 是cursor的起始位置，包括文件名字之类的，但不是范围。offset距离文件头的偏移位置。
        # l = cursor.location
        # logging.info("file=%s, line=%d, column=%d, offset=%d" % (l.file, l.line, l.column, l.offset))
        logging.info("%d, %s, %s, %s" % (cursor.location.line, cursor.spelling, cursor.displayname, cursor.brief_comment))

        self.graph.add_edge(parent_result, self.num)
        self.num += 1

        return self.num - 1

    def _print(self, cursor, level):
        # if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
        ''' 打印出cursor的信息。'''
        print '-' * level + '%s, %s [line=%s, col=%s]' % \
            (cursor.kind, cursor.spelling, cursor.location.line, cursor.location.column)

    def show(self):
        ''' 显示整个节点树 '''

        # 可以显示出来，或者保存成文件。
        # logging.info(self.graph.string())
        # graph.write('simple.dot')  # write to simple.dot
        # B = pgv.AGraph('simple.dot')  # can create a new graph from file

        # 显示为图形，并打开。(也可以用dot命令将 *.dot 文件变成图片，然后显示处理，dot文件可以认为矢量的。)
        self.graph.layout('dot')  # layout with default (neato), dot is directed graphs.
        self.graph.draw(self.path)  # draw png
        # subprocess.call('eog %s' % self.path, shell=True, executable="/bin/bash")

def travel_source(parent_cursor, parent_result, cursor, visitor, level):
    """ 分析指定的cursor内的代码，用层级显示节点之间的包含关系。
    @param cursor: Cursor: as a node
    """

    # print '-' * level + '%s, %s [line=%s, col=%s]' % \
    #    (cursor.kind, cursor.spelling, cursor.location.line, cursor.location.column)
    is_continue, result = visitor.process(parent_cursor, parent_result, cursor, level)
    if not is_continue:
        return

    # Recurse for children of this cursor
    for c in cursor.get_children():
        travel_source(cursor, result, c, visitor, level + 1)

    if level == 0:
        visitor.finish()

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
    graph = pgv.AGraph(directed=True)

    # node's attributes: http://www.graphviz.org/doc/info/attrs.html
    # label中可以加入中文，只是需要 u""。
    graph.add_node('1', color='red', fillcolor='green', label=u'罗春雷')

    graph.add_edge('1', 2)
    graph.add_edge(2, 3)
    graph.add_edge('1', 3)

    # 可以显示出来，或者保存成文件。
    logging.info(graph.string())
    # graph.write('simple.dot')  # write to simple.dot
    # B = pgv.AGraph('simple.dot')  # can create a new graph from file

    # 显示为图形，并打开。(也可以用dot命令将 *.dot 文件变成图片，然后显示处理，dot文件可以认为矢量的。)
    graph.layout('dot')  # layout with default (neato), dot is directed graphs.
    graph.draw(path)  # draw png
    subprocess.call('eog %s' % path, shell=True, executable="/bin/bash")

def show_nodes_original(cursor):

    # 生成临时文件。
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)

    # 形成节点
    graph = pgv.AGraph(directed=True)

    # node's attributes: http://www.graphviz.org/doc/info/attrs.html
    # label中可以加入中文，只是需要 u""。
    graph.add_node('1', color='red', fillcolor='green', label=u'罗春雷')

    graph.add_edge('1', 2)
    graph.add_edge(2, 3)
    graph.add_edge('1', 3)

    # 可以显示出来，或者保存成文件。
    logging.info(graph.string())
    graph.write('simple.dot')  # write to simple.dot
    # B = pgv.AGraph('simple.dot')  # can create a new graph from file

    # 显示为图形，并打开。(也可以用dot命令将 *.dot 文件变成图片，然后显示处理，dot文件可以认为矢量的。)
    graph.layout('dot')  # layout with default (neato), dot is directed graphs.
    graph.draw(path)  # draw png
    subprocess.call('eog %s' % path, shell=True, executable="/bin/bash")

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
    # print 'Translation unit:', tu.spelling

    # 分析代码
    # analysis_source(tu.cursor)
    # show_nodes(tu.cursor)
    travel_source(None, None, tu.cursor, VisitorGraph(file_path), 0)

    # 检索文件中的节点和 type_name 相关的。
    # find_typerefs(tu.cursor, type_name, 0)

if __name__ == "__main__":
    # set the level of log.
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    # Usage: call with <file_name: string: 需要分析的文件的路径> <type_name: string: 程序中具体的类型名字>
    main("/home/luocl/myprojects/AgileEditor/ae/src/test.cpp", 'my_print')
