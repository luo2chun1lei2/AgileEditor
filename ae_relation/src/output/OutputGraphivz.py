# -*- coding:utf-8 -*-

# output
# 用Graphviz来输出结果。

import logging, shutil

from .Output import *
from misc import *

class TravelElements(object):
    # Travel Elements to create some thing
    # use Graphivz to create Element and Relation diagram
    
    def __init__(self):
        super(TravelElements, self).__init__()
        
        self.graphivz = Graphivz()
        self.data_fd, self.data_path = Utils.create_tmpfile("txt")
        logging.debug("Create tmp input_file:%s" % self.data_path)
        
        self._write("digraph element_and_relation {\n")
    
    def _write(self, str):
        # 会在字符串后面加入空格。
        os.write(self.data_fd, "%s\n" % str)
    
    def travel(self, elements):
        # @param elements: AElement[]: set of all needed elements.
        # @return bool: True is ok, False is failed.
        
        os.write(self.data_fd, "Hello->World\n")

        # TODO: 下面的方法是否应该挪入到各个 element 中实现？但是这个和具体的view相关。
#         for e in elements:
#             if isinstance(e, UMLClass):
#                 text = "class %s " % e.title
#                 if e.color:
#                     text += " #%s" % e.color
#                 text += " {\n"
#                 for field_name, field_type in e.fields:
#                     text += "%s : %s\n" % (field_name, field_type)
#                 text += "}"
#                 
#                 self._write(text)
#                 
#             elif isinstance(e, UMLComponent):
#                 # component的名字用[]来包括。
#                 text = "component [%s] as [%s]" % \
#                         (util_trip_quoted_name(e.title), \
#                          util_trip_quoted_name(e.name))
#                 if e.color:
#                     text += " #%s" % e.color
#                 self._write(text)
#                 
#             elif isinstance(e, UMLClassRelation):
#                 type_element, title, from_element, to_element = e.get_relation()
#                 if type_element == 'Extension': # TODO: 继承不需要额外的名字。
#                     text = "%s --|> %s" % (from_element.name, to_element.name)
#                 elif type_element == 'Composition':
#                     text = "%s *-- %s" % (from_element.name, to_element.name)
#                 elif type_element == 'Aggregation':
#                     text = "%s o-- %s" % (from_element.name, to_element.name)
#                 else:
#                     print "Don't recognize this type_element \"%s\" of class relation" % type_element
#                     return False
#                 
#                 if e.title:
#                     text += ": %s" % (e.title)
#                 
#                 self._write(text)
#             
#             if isinstance(e, UMLComponentRelation):
#                 type_element, title, from_element, to_element = e.get_relation()
#                 text = ""
#                 if type_element == 'Use':
#                     # component的名字用[]来包括。
#                     text = "[%s] ..> [%s]" % \
#                         (util_trip_quoted_name(from_element.name), \
#                          util_trip_quoted_name(to_element.name))
#                 else:
#                     print "Don't recognize this type_element \"%s\" of class relation" % type_element
#                     return False
#                 
#                 if title:
#                     text += " : %s" % (title)
#             
#                 self._write(text)
                
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

