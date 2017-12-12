#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
技术研究：
    1，clang分析代码。采用“clang.cindex"，是libclang的python接口。
    2，graphviz来显示流程和关系。
      为了使用graphviz，需要安装“python-pygraphviz”，参考网站“http://pygraphviz.github.io/”。
      为了显示 dot 文件，需要安装 "xdot" 程序。
设计方案：
    1，可以显示任一函数或者文件的内部的节点图。
    2，可以分析其中一个函数的运行路线。
    3，建立某个子系统的状态切换是否正确。
    4，根据运行路线，核对是否状态切换正确。
'''

import sys, os, logging, subprocess, tempfile
import clang.cindex as cindex
import pygraphviz as pgv

class Visitor(object):
    def __init__(self, file_path, func_name, args):
        super(Visitor, self).__init__()
        
        self.file_path = file_path
        self.func_name = func_name
        self.args = args

    def start(self):
        ''' 开始，做准备用的。 '''
        pass

    def process(self, parent_cursor, parent_result, cursor, level):
        ''' 接受节点进行处理
        @param parent_cursor: Cursor: 父节点
        @param cursor: Cursor: 当前的节点
        @param level: int: 陷入的层次
        @return (is_continue:bool:True,继续进行，False,不再继续深入, result:object:附带结果，传给下面的节点) 。
        '''
        return True, None

    def finish(self):
        ''' 遍历节点完成，自行决定返回值 '''
        return None

class VisitorGraph(Visitor):
    ''' 遍历Cursor，并用Graphviz显示节点关系。
    '''
    def __init__(self, file_path, func_name, args):
        '''
        @param file_path: string: 文件的名字[必须]
        @param func_name: string: 函数的名字[可选]
        '''
        super(VisitorGraph, self).__init__(file_path, func_name, args)

        # 创建Graph
        self.graph = pgv.AGraph(directed=True)
        self.graph.graph_attr['epsilon'] = '0.001'
        # self.graph.graph_attr['rankdir'] = 'LR'  # 从左到右排列。
        # self.graph.node_attr['shape'] = 'record'  # 每个节点自定义

        self.num = 1

    # override from Visitor
    def start(self):
        pass

    # override from Visitor
    def process(self, parent_cursor, parent_result, cursor, level):
        result = self._add_2_graph(parent_result, cursor, level)
        return True, result

    # override from Visitor
    def finish(self):
        ''' 遍历节点完成 '''
        self._show()
        return None

    def _add_2_graph(self, parent_result, cursor, level):
        ''' 必须是指定的文件，include进来的，不算。
        @return (int:层级, bool:是否匹配检索需要)
        '''
        if parent_result is None:
            parent_no = 0
            parent_found = False
        else:
            parent_no, parent_found = parent_result

        # 查看是否是指定的文件
        if cursor.location.file is None or self.file_path != cursor.location.file.name:
            # 不是
            return 0, False

        # 查看是否是指定的函数。
        found = False
        if parent_found == True:
            found = True
        else:
            if self.func_name is None:
                # 如果函数名字空，那么解析所有的节点。
                found = True
            else:
                # 如果函数名字不是空，那么需要比对是否定义和名字是否相等。
                if cursor.kind.is_declaration() and cursor.spelling == self.func_name:
                    logging.info("find declaration %s" % self.func_name)
                    found = True

        if found:
            # 需要绘制
            shape = 'record'
            if cursor.kind == cindex.CursorKind.IF_STMT:
                shape = 'diamond'

            # extent 是cursor的代码范围(SourceRange)，start和end都是SourceLocation
            # cursor.type 是语法分析后得到的节点的语法类型（比如int），如果有的话。
            e = cursor.extent
            self.graph.add_node(self.num, shape=shape, fontcolor='white', color='black', fillcolor='royalblue1', style='filled',
                                label="%s, %d:%d~%d:%d, %s" % (cursor.kind.name, e.start.line, e.start.column, e.end.line, e.end.column, cursor.spelling))

            # cursor.location(SourceLocation) 是cursor的起始位置，包括文件名字之类的，但不是范围。offset距离文件头的偏移位置。
            # l = cursor.location
            # logging.info("file=%s, line=%d, column=%d, offset=%d" % (l.file, l.line, l.column, l.offset))
            logging.info("%d, %s, %s, %s" % (cursor.location.line, cursor.spelling, cursor.displayname, cursor.brief_comment))

            self.graph.add_edge(parent_no, self.num)

        self.num += 1
        return self.num - 1, found

    def _print(self, cursor, level):
        # if cursor.kind == cindex.CursorKind.TRANSLATION_UNIT:
        ''' 打印出cursor的信息。'''
        print '-' * level + '%s, %s [line=%s, col=%s]' % \
            (cursor.kind, cursor.spelling, cursor.location.line, cursor.location.column)

    def _show(self, format=None):
        ''' 显示整个节点树
        @param format: string: None是缺省显示为svg.
        '''
        
        if format == 'console':
            # 显示到控制台
            logging.info(self.graph.string())
        elif format == 'dot':
            path = self._create_tmpfile('dot')
            # 保存为dot文件。
            self.graph.write(path)
            subprocess.call('xdot %s' % path, shell=True, executable="/bin/bash")
        elif format == 'png':
            # 显示为图形，并打开。(也可以用dot命令将 *.dot 文件变成图片，然后显示处理，dot文件可以认为矢量的。)
            path = self._create_tmpfile('png')
            self.graph.layout('dot')  # layout with default (neato), dot is directed graphs.
            self.graph.draw(path)  # draw png
            subprocess.call('eog %s' % path, shell=True, executable="/bin/bash")
        else: # svg
            # 保存为svg文件。
            path = self._create_tmpfile('svg')
            self.graph.layout('dot')
            self.graph.draw(path, format='svg')
            subprocess.call('eog %s' % path, shell=True, executable="/bin/bash")
        
    def _create_tmpfile(self, suffix):
        # 生成临时文件。
        fd, path = tempfile.mkstemp(suffix = (".%s" % suffix))
        os.close(fd)
        return path
    
class Node(object):
    ''' 节点（包括指向父节点和子节点等），为了方便能够计算运行流程。
    '''
    def __init__(self, parent_node, cursor):
        super(Node, self).__init__()
        # 父节点(Node)
        self.parent = parent_node
        # 自己的子节点([Node])
        self.children = []
        # 自己对应的cursor(cindex.Cursor)
        self.cursor = cursor
    
    def add_child_node(self, node):
        self.children.append(node)
        
    def info(self):
        if self.parent is None:
            return "This is root node."
        else:
            e = self.cursor.extent
            return '%s %d:%d~%d:%d %s' % \
                (self.cursor.kind.name, 
                 e.start.line, e.start.column, e.end.line, e.end.column, 
                 self.cursor.spelling)
    
class VisitorTree(Visitor):
    ''' 生成新的节点树
    '''
    def __init__(self, file_path, func_name, args):
        super(VisitorTree, self).__init__(file_path, func_name, args)

    def start(self):
        ''' 开始，做准备用的。 '''
        # 根节点
        self.root = Node(None, None)

    def process(self, parent_cursor, parent_result, cursor, level):
        ''' 接受节点进行处理
        @param parent_cursor: Cursor: 父节点
        @param cursor: Cursor: 当前的节点
        @param level: int: 陷入的层次
        @return (is_continue:bool:True,继续进行，False,不再继续深入, result:object:附带结果，传给下面的节点) 。
        '''
        parent_node = parent_result
        
        node = Node(parent_node, cursor)
        if parent_node is None:
            # 首节点可能没有parent node。
            node = self.root
        else:
            parent_node.add_child_node(node)
        
        return True, node

    def finish(self):
        ''' 遍历节点完成 '''
        return self.root

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
    
def analysis_code(visitor):
    ''' 分析代码，并显示代码的AST。
    @param file_path: string: module's path
    @param args: [sring]: compilation arguments, such as "["-I/home/luocl/myprojects/abc"]"
    @param func_name: string: function's name
    '''
    # 生成核心的Index实例
    index = cindex.Index.create()
    # 用Index分析代码，这里是一个文件。
    tu = index.parse(visitor.file_path, visitor.args)

    # 分析代码
    
    visitor.start() # 开始函数
    travel_source(None, None, tu.cursor, visitor, 0)
    return visitor.finish() # 结束函数
    
def travel_node_tree(node):
    ''' 遍历节点树
    '''
    logging.info("node %s" % node.info())
    
    for child in node.children:
        travel_node_tree(child)
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    # Usage: call with <file_path: string: 需要分析的文件的路径> <type_name: string: 程序中具体的类型名字>
    visitor = VisitorTree("/home/luocl/myprojects/AgileEditor/ae/src/test.cpp",
                           'test_mem', ["-I/home/luocl/myprojects/abc"])
    node = analysis_code(visitor)
    
    travel_node_tree(node)
