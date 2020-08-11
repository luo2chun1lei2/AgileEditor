# -*- coding:utf-8 -*-

# output
# 用Graphviz来输出结果。

import logging, shutil

from .Output import *
from misc import *
from model import *

class TravelElements(object):
    # Travel Elements to create some thing
    # use Graphivz to create Element and Relation diagram
    
    def __init__(self):
        super(TravelElements, self).__init__()
        
        self.graphivz = Graphivz()
        self.data_fd, self.data_path = Utils.create_tmpfile("txt")
        logging.debug("Create tmp input_file:%s" % self.data_path)
        
        # "digraph" 表示有向图。无向图是 "graph"
        self._write("digraph element_and_relation {  \n")
    
    def _write(self, str):
        # 会在字符串后面加入空格。
        os.write(self.data_fd, "%s\n" % str)
    
    def travel(self, elements):
        # @param elements: AElement[]: set of all needed elements.
        # @return bool: True is ok, False is failed.
        
        for e in elements:
            if isinstance(e, Relation):
                from_element = e.elements[0]
                to_element = e.elements[1]
                type = e.relation_type
                title = e.title
                text = "%s -> %s" % (from_element.name, to_element.name)
                 
                text += "["
                if e.title:
                    text += "label=\"%s\", " % (title)
                    
                if type == "type":
                    text += "dir=\"both\", arrowtail=\"onormal\", arrowhead=\"none\", "
                elif type == "depend":
                    text += "" # 使用缺省的箭头。
                elif type == "own":
                    text += "dir=\"both\", arrowtail=\"diamond\", arrowhead=\"vee\","
                
                text += "];"

                self._write(text)
            elif isinstance(e, Element):
                text = "%s [" % (e.name)
                
                if e.title != None:
                    text += " label=\"%s\"," % (e.title)
                    
                type = e.element_type
                if type == "type":
                    text += " shape=diamond,"
                elif type == "function":
                    text += " shape=ellipse,"
                else: #type == "instance":
                    text += " shape=box,"
                    
                text += "];"
                self._write(text)
                
        return True
    
    def finish(self):
        # finish travel
        self._write("\n}")
        
        os.close(self.data_fd)
        out_dir = Utils.create_tmpdir()
    
        self.graphivz.create_diagram(self.data_path, out_dir + "/123.dot")  # TODO:名字？
    
        # - remove all temporary files and directories.
        os.remove(self.data_path)
        shutil.rmtree(out_dir)

class OutputGraphviz(object):
    def __init__(self):
        super(OutputGraphviz, self).__init__()
        
    def show(self, model, cmdPkg):
        # 显示信息
        # @param info string 输出的类型是下面的各种。
        #    dot - filter for drawing directed graphs
        #    neato - filter for drawing undirected graphs
        #    twopi - filter for radial layouts of graphs
        #    circo - filter for circular layout of graphs
        #    fdp - filter for drawing undirected graphs
        #    sfdp - filter for drawing large undirected graphs
        #    patchwork - filter for squarified tree maps
        #    osage - filter for array-based layouts 
        
        # 1. 遍历数据，得到显示用的数据结构
        # 2. 根据显示用的数据结构，输出。
        travel = TravelElements()
        
        travel.travel(model.elements.values())
        
        # 遍历后，显示出来。
        travel.finish()

