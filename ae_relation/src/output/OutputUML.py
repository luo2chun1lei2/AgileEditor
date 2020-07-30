# -*- coding:utf-8 -*-

# output
# 输出的基础类。

import logging

from .Output import *
from model.concrete.UMLModel import *
from misc import *
    
class TravelElements(object):
    # Travel Elements to create some thing
    # use PlantUML to create class and component diagram
    
    def __init__(self):
        super(TravelElements, self).__init__()
        
        self.uml = PlantUML(util_get_exe_dir() + "/plantuml/plantuml.jar")
        self.data_fd, self.data_path = Utils.create_tmpfile("txt")
        logging.debug("Create tmp input_file:%s" % self.data_path)
        
        self._write("@startuml")
    
    def _write(self, str):
        # 会在字符串后面加入空格。
        os.write(self.data_fd, "%s\n" % str)
    
    def travel(self, elements):
        # @param elements: AElement[]: set of all needed elements.
        # @return bool: True is ok, False is failed.
        
        # TODO: 下面的方法是否应该挪入到各个 element 中实现？但是这个和具体的view相关。
        for e in elements:
            if isinstance(e, UMLClass):
                text = "class %s " % e.title
                if e.color:
                    text += " #%s" % e.color
                text += " {\n"
                for field_name, field_type in e.fields:
                    text += "%s : %s\n" % (field_name, field_type)
                text += "}"
                
                self._write(text)
                
            elif isinstance(e, UMLComponent):
                # component的名字用[]来包括。
                text = "component [%s] as [%s]" % \
                        (util_trip_quoted_name(e.title), \
                         util_trip_quoted_name(e.name))
                if e.color:
                    text += " #%s" % e.color
                self._write(text)
                
            elif isinstance(e, UMLClassRelation):
                type_element, title, from_element, to_element = e.get_relation()
                if type_element == 'Extension': # TODO: 继承不需要额外的名字。
                    text = "%s --|> %s" % (from_element.name, to_element.name)
                elif type_element == 'Composition':
                    text = "%s *-- %s" % (from_element.name, to_element.name)
                elif type_element == 'Aggregation':
                    text = "%s o-- %s" % (from_element.name, to_element.name)
                else:
                    print "Don't recognize this type_element \"%s\" of class relation" % type_element
                    return False
                
                if e.title:
                    text += ": %s" % (e.title)
                
                self._write(text)
            
            if isinstance(e, UMLComponentRelation):
                type_element, title, from_element, to_element = e.get_relation()
                text = ""
                if type_element == 'Use':
                    # component的名字用[]来包括。
                    text = "[%s] ..> [%s]" % \
                        (util_trip_quoted_name(from_element.name), \
                         util_trip_quoted_name(to_element.name))
                else:
                    print "Don't recognize this type_element \"%s\" of class relation" % type_element
                    return False
                
                if title:
                    text += " : %s" % (title)
            
                self._write(text)
                
        return True
    
    def finish(self):
        # finish travel
        self._write("@enduml")
        
        os.close(self.data_fd)
        out_dir = Utils.create_tmpdir()
    
        self.uml.create_diagram(self.data_path, out_dir)
    
        # - remove all temporary files and directories.
        os.remove(self.data_path)
        shutil.rmtree(out_dir)

class ShowSequence(TravelElements):
    # Travel Elements to create SEQUENCE diagram.
    # use PlantUML. 需要顺序。
    
    def __init__(self):
        super(ShowSequence, self).__init__()
        
    def travel_component(self, elements):
        # participants: []: 所有的参与者
        participants = []
        seq = {}
        for e in elements:
            if isinstance(e, UMLClass) or isinstance(e, UMLComponent):
                participants.append(e)
                
                text = "participant \"%s\" " % e.title
                text += " as %s" % e.name
                if e.color:
                    text += " #%s" % e.color
                
                seq[e.no] = text
        
        for l in sorted(seq):
            self._write(seq[l])
        
        return True
    
    def travel_invoke(self, elements):
        # invokes: []: 所有的调动关系
        invokes = []
        seq_info = {}
        for e in elements:
            if isinstance(e, UMLMethodRelation):
                invokes.append(e)
                
                type_element, from_parent, from_element, to_parent, to_element = e.get_relation()
                text = "%s -> %s : %s" % (from_parent.name, to_parent.name, to_element.name)
                seq_info[e.no] = (to_parent, text)

        
        last_to = None
        for l in sorted(seq_info):
            to_parent, text = seq_info[l]
            
            if last_to is not to_parent:
                if last_to is not None:
                    self._write("deactivate %s" % last_to.name)
                self._write("activate %s" % to_parent.name)
                last_to = to_parent
            
            self._write(text)
            
        return True
        
    def travel(self, elements):
        # 先找到所有的invoke关系，然后按照顺序再找到相关的组件。
        
        self.travel_component(elements)
        self.travel_invoke(elements)
        
        self._write("hide footbox")
        return True
        
    # TODO :  不用了。
    def travel1(self, elements):
        # @param elements: AElement[]: set of all needed elements.
        # @return bool: True is ok, False is failed.
        
        pre_texts = {}
        post_texts = {}
        
        for e in elements:
            if isinstance(e, UMLClass) or isinstance(e, UMLComponent):
                # ex: participant "I have a really\nlong name" as L #99FF99
                text = "participant \"%s\" " % e.title
                text += " as %s" % e.name
                if e.color:
                    text += " #%s" % e.color

                pre_texts[e.no] = text
                
            elif isinstance(e, UMLClassRelation) or isinstance(e, UMLComponentRelation):
                # ex: Alice->Bob: Authentication Request
                type_element, title, from_element, to_element = e.get_relation()
                if type_element == 'Use': # TODO: 继承不需要额外的名字。
                    text = "%s -> %s : %s" % (from_element.name, to_element.name, title)
                else:
                    print "Don't recognize this type_element \"%s\" of relation." % type_element
                    return False
                 
                if e.title:
                    text += ": %s" % (e.title)
                post_texts[e.no] = text
                
            elif isinstance(e, UMLElement2MethodRelation):
                # 找到函数
                # ex: Alice->Bob: Authentication Request
                type_element, title, from_element, to_element = e.get_relation()
                if type_element == 'Use': # TODO: 继承不需要额外的名字。
                    text = "%s -> %s : %s" % (from_element.name, to_element.name, title)
                else:
                    print "Don't recognize this type_element \"%s\" of relation." % type_element
                    return False
                
                if e.title:
                    text += ": %s" % (e.title)
                post_texts[e.no] = text
                
        for l in sorted(pre_texts):
            self._write(pre_texts[l])
        
        for l in sorted(post_texts):
            self._write(post_texts[l])

        self._write("hide footbox")
        return True

class OutputUML(Output):
    def __init__(self):
        super(Output, self).__init__()
        
    def show(self, model, cmdPkg):
        logging.debug("show diagram of model.")
        
        diagram_type = cmdPkg.diagram
        
        if diagram_type in ( "class", "component"): 
            travel = TravelElements()
        elif diagram_type in ("sequence", "seq"):
            travel = ShowSequence()
        else:
            travel = TravelElements()

        travel.travel(model.elements.values())
        travel.finish()
