#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
技术研究：
    1，clang分析代码。采用“clang.cindex"，是libclang的python接口。
        Clang之语法抽象语法树AST ： https://www.cnblogs.com/zhangke007/p/4714245.html
        clang static analyzer源码分析（一）～ （五） ： http://blog.csdn.net/dashuniuniu/article/category/6013535
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

''' #################################################################
    Cursor
'''

class Visitor(object):
    def __init__(self, file_path, args):
        super(Visitor, self).__init__()

        self.file_path = file_path
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
        super(VisitorGraph, self).__init__(file_path, args)
        self.func_name = func_name

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
                    logging.debug("find declaration %s" % self.func_name)
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
                                label="{%s|%d:%d~%d:%d, %s}" % (cursor.kind.name, e.start.line, e.start.column, e.end.line, e.end.column, cursor.spelling))

            # cursor.location(SourceLocation) 是cursor的起始位置，包括文件名字之类的，但不是范围。offset距离文件头的偏移位置。
            # l = cursor.location
            # logging.info("file=%s, line=%d, column=%d, offset=%d" % (l.file, l.line, l.column, l.offset))
            logging.info("%s %d:%d %s" % \
                (cursor.kind.name, cursor.location.line, cursor.location.column, cursor.spelling))

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
        else:  # svg
            # 保存为svg文件。
            path = self._create_tmpfile('svg')
            self.graph.layout('dot')
            self.graph.draw(path, format='svg')
            subprocess.call('eog %s' % path, shell=True, executable="/bin/bash")

    def _create_tmpfile(self, suffix):
        # 生成临时文件。
        fd, path = tempfile.mkstemp(suffix=(".%s" % suffix))
        os.close(fd)
        return path

def show_crusor_tree():
    ''' 显示cursor的图 '''
    visitor = VisitorGraph("/home/luocl/myprojects/AgileEditor/ae/test/test.cpp",
                           'test_mem', ["-I/home/luocl/myprojects/abc"])
    analysis_code(visitor)

''' #################################################################
    节点
'''

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

        # 供每个功能建立自己的属性。在此外不保证保留数据和清理数据。
        self.properties = {}

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
    ''' 遍历整个Cursor生成Node Tree。
    '''
    def __init__(self, file_path, args):
        super(VisitorTree, self).__init__(file_path, args)

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
    visitor.start()  # 开始函数
    travel_source(None, None, tu.cursor, visitor, 0)
    return visitor.finish()  # 结束函数

class NodeVisitor(object):
    def __init__(self):
        super(NodeVisitor, self).__init__()

    def process(self, node):
        pass

def travel_node_tree(node, visitor):
    ''' 遍历节点树
    '''
    visitor.process(node)

    for child in node.children:
        travel_node_tree(child, visitor)

def show_node_tree(node):
    class NodeVisitorInfo(NodeVisitor):
        def __init__(self):
            super(NodeVisitorInfo, self).__init__()

        def process(self, node):
            logging.info("node %s" % node.info())

    travel_node_tree(node, NodeVisitorInfo())

def find_node_of_func(node, func_name):
    '''
    @param func_name: string: function name
    '''
    class NodeVisitorFind(NodeVisitor):
        def __init__(self, func_name):
            super(NodeVisitorFind, self).__init__()
            self.func_name = func_name
            self.found = None

        def process(self, node):
            cursor = node.cursor
            if cursor is not None:
                if cursor.kind.is_declaration() and cursor.spelling == self.func_name:
                    logging.debug("found declaration.")
                    # 因为函数的定义和声明在这里都是声明，所以需要看此节点的子节点是否有COMPOUND_STMT，
                    # 就是函数定义的大括号，如果没有这个就可以认为没有定义。
                    for child in node.children:
                        if child.cursor.kind == cindex.CursorKind.COMPOUND_STMT:
                            self.found = node

    visitor = NodeVisitorFind(func_name)
    travel_node_tree(node, visitor)
    return visitor.found

def show_node_graph(node):
    ''' 显示节点的graph '''
    if node is None:
        return

    class NodeVisitorGraphviz(NodeVisitor):
        def __init__(self):
            super(NodeVisitorGraphviz, self).__init__()

            self.graph = pgv.AGraph(directed=True)
            self.graph.graph_attr['epsilon'] = '0.001'

            # 作为graphviz的每个节点的标号，必须是唯一的。
            self.num = 1

        def _get_content(self, extent):
            # TODO 有些函数太长了。
            fd = open(extent.start.file.name)
            fd.seek(extent.start.offset)
            str = fd.read(extent.end.offset - extent.start.offset)
            fd.close()
            return str

        def _escape_label(self, s):
            return s.replace("\\", "\\\\").replace("{", r"\{").replace("}", r"\}").replace("<", r"\<").replace(">", r"\>")

        def process(self, node):
            shape = 'Mrecord'  # 带有圆角的矩形。
            cursor = node.cursor
            e = cursor.extent

            if cursor.kind == cindex.CursorKind.IF_STMT:
                shape = 'Mrecord'

            no = self._create_no()
            node.properties['no'] = no

            # 添加节点
            # - label 如果想用HTML语法，必须用 "<?>" 形式。而“<f0>??”不是HTML语法，而是子标记。
            # logging.info(">>> %s" % self._escape_label(self._get_content(e)))
            self.graph.add_node(no, shape=shape, fontcolor='white', color='black', fillcolor='royalblue1', style='filled',
                                label="{%s|%d:%d~%d:%d|%s}" % \
                                (cursor.kind.name, e.start.line, e.start.column, e.end.line, e.end.column,
                                self._escape_label(self._get_content(e))))

            # 添加节点之间的边。
            if 'no' in node.parent.properties:
                parent_no = node.parent.properties['no']
            else:
                parent_no = 0
            self.graph.add_edge(parent_no, no)

        def _create_no(self):
            self.num += 1
            return self.num

        def _create_tmpfile(self, suffix):
            # 生成临时文件。
            fd, path = tempfile.mkstemp(suffix=(".%s" % suffix))
            os.close(fd)
            return path

        def show(self):
            path = self._create_tmpfile('svg')
            self.graph.layout('dot')
            self.graph.draw(path, format='svg')
            subprocess.call('eog %s' % path, shell=True, executable="/bin/bash")

    visitor = NodeVisitorGraphviz()
    travel_node_tree(node, visitor)

    visitor.show()

def clean_node_tree(node):
    ''' 清理node tree中的properties。 '''
    class NodeVisitorClean(NodeVisitor):
        def __init__(self):
            super(NodeVisitorClean, self).__init__()

        def process(self, node):
            node.properties.clear()

    travel_node_tree(node, NodeVisitorClean())

class NodePath(object):
    ''' 建立Node的Path路径。 '''
    def __init__(self):
        super(NodePath, self).__init__()
        # 节点列表 [Node]
        self.nodes = []

def find_path_of_node(node):
    ''' 根据node找到可能的path
    1, 简单的算法是只要是分支，就算两个分支。循环算一个分支。
       调用子函数不管。
    2，复杂的算法是根据输入的值，来判断是否真的可以走到这些分支。
        循环类似。调用子函数需要到内部分析。
        还允许对函数进行标记。
    '''

    if node is None:
        return

    class NodeVisitorFindPathes(NodeVisitor):
        ''' 遍历NodeTree，找到里面所有的Path '''
        def __init__(self):
            super(NodeVisitorFindPathes, self).__init__()
            self.pathes = []

        def process(self, node):
            pass

        def show(self):
            path = self._create_tmpfile('svg')
            self.graph.layout('dot')
            self.graph.draw(path, format='svg')
            subprocess.call('eog %s' % path, shell=True, executable="/bin/bash")

    visitor = NodeVisitorFindPathes()
    travel_node_tree(node, visitor)

    return visitor.pathes

def process_source():
    # 分析代码得到一个节点树
    # Usage: call with <file_path: string: 需要分析的文件的路径> <type_name: string: 程序中具体的类型名字>
    visitor = VisitorTree("/home/luocl/myprojects/AgileEditor/ae/test/test.cpp",
                           ["-I/home/luocl/myprojects/abc"])
    root_node = analysis_code(visitor)

    # 遍历节点树，显示节点树的信息。
    show_node_tree(root_node)

    # 找到需要的函数定义
    found_node = find_node_of_func(root_node, "test_print")
    if found_node is None:
        logging.error("Don't find function declaration.")
        sys.exit(1)
    else:
        logging.info("found function defination: %s" % found_node.info())

    # 显示函数的AST关系图。
    show_node_graph(found_node)

    clean_node_tree(root_node)

    # 分析此函数的所有的路径。
    pathes = find_path_of_node(found_node)
    if len(pathes) == 0:
        logging.error("Cannot find one path.")
        sys.exit(1)

    # 显示其中一条路径的调用关系图

    # 计算每个路径的结果。

''' #################################################################
    main
'''

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')

    # show_crusor_tree()
    process_source()
