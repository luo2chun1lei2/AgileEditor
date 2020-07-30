# -*- coding:utf-8 -*-

# UML的相关 Element和Relation

import os, sys, logging, getopt, shutil, traceback

from misc import *

from model.Relation import *
from model.Element import *
from model.Model import *

class UMLComponent(AElement):
    # UML's component
    def __init__(self, name, no, title, color=None):
        super(UMLComponent, self).__init__("Component", name, no)
        self.fields = []
        self.methods = []
        self.color = color
        if title:
            self.title = title
        else:
            self.title = name

    def add_field(self, field_name, field_type):
        self.fields.append((field_name, field_type))
    
    # TODO: should change to relation.
    def add_method(self, method):
        # method: UMLMethod
        self.methods.append(method)
        
#     def get_method(self, method_name):
#         if method_name in self.methods:
#             return self.methods[method_name]

class UMLClass(AElement):
    # UML's class
    def __init__(self, name, no, title, color=None):
        super(UMLClass, self).__init__("Class", name, no)
        self.fields = []
        self.methods = {}
        self.color = color
        if title:
            self.title = title
        else:
            self.title = name

    def add_field(self, field_name, field_type):
        self.fields.append((field_name, field_type))
    
    def add_method(self, method):
        # method: UMLMethod
        self.methods.append(method)
    
#     def get_method(self, method_name):
#         if method_name in self.methods:
#             return self.methods[method_name]

class UMLMethod(AElement):
    # UML's method
    def __init__(self, name, no, title, parent, color=None):
        # TODO:这里category，有可能重复，因为函数有可能在不同的类或者component中重名。
        # parent: AELement: 是此方法所在的模块，如果是None，那么将是全局空间的。
        super(UMLMethod, self).__init__(parent.name, name, no)
        self.fields = []
        self.returns = []
        self.color = color
        if title:
            self.title = title
        else:
            self.title = name
        
        self.parent = parent

    def add_argument(self, aug_name, arg_type):
        # 添加参数。
        self.fields.append((aug_name, arg_type))
        
    def add_return(self, arg_name, arg_type):
        # 添加返回值，比如python，允许返回多个值
        self.returns.append((arg_name, arg_type))

# TODO: relation 是否应该区分 class 还是 component，虽然有不同的type，但是实现方面是没有什么区别的
# 是有不同的。
class UMLClassRelation(ARelation):
    # 类和类之间的关系
    def __init__(self, name, no):
        super(UMLClassRelation, self).__init__("ClassRelation", name, no)

    def set_relation(self, relation_type, title, from_element, to_element):    # TODO 此处参数是否应该不定个数?
        # @param from_element:AElement:
        # @param title: string:
        # @param to_element:AElement:
        # @param relation_type:string: Extension/Composition/Aggregation
        self.from_element = from_element
        self.to_element = to_element
        self.relation_type = relation_type
        self.title = title
    
    def get_relation(self):
        # relation_type: string
        # from_element: AElement
        # to_element: AElement
        return self.relation_type, self.title, self.from_element, self.to_element 
        
class UMLComponentRelation(ARelation):
    # 组件之间的关系
    def __init__(self, name, no):
        super(UMLComponentRelation, self).__init__("ComponentRelation", name, no)

    def set_relation(self, relation_type, title, from_element, to_element):
        # @param from_element:AElement:
        # @param title: string
        # @param to_element:AElement:
        # @param relation_type:string: Use
        self.from_element = from_element
        self.to_element = to_element
        self.relation_type = relation_type
        self.title = title
    
    def get_relation(self):
        # relation_type: string
        # title: string
        # from_element: AElement
        # to_element: AElement
        return self.relation_type, self.title, self.from_element, self.to_element
    
class UMLElement2MethodRelation(ARelation):
    # 其他元素和函数之间的关系。单向关系。
    def __init__(self, name, no):
        super(UMLElement2MethodRelation, self).__init__("Element2MethodRelation", name, no)

    def set_relation(self, relation_type, title, from_element, to_element):
        # @param relation_type: string: Have/  [一般函数和静态函数关系]
        # @param title: string
        # @param from_element:AElement:
        # @param to_element:UMLMethod:
        self.from_element = from_element
        self.to_element = to_element
        self.relation_type = relation_type
        self.title = title
    
    def get_relation(self):
        # relation_type: string
        # title: string
        # from_element: AElement
        # to_element: AElement
        return self.relation_type, self.title, self.from_element, self.to_element
    
class UMLMethodRelation(ARelation):
    # 函数之间的关系，基本上就是调用。
    def __init__(self, name, no):
        super(UMLMethodRelation, self).__init__("MethodRelation", name, no)

    def set_relation(self, relation_type, from_parent, from_element, to_parent, to_element):
        # @param from_parent:AElement:
        # @param from_method:AElement:
        # @param to_parent:AElement:
        # @param to_element:AElement:
        # @param to_method:string: Invoke
        
        self.relation_type = relation_type
        self.from_parent = from_parent
        self.from_element = from_element
        self.to_parent = to_parent
        self.to_element = to_element
    
    def get_relation(self):
        # relation_type: string
        # from_element: AElement
        # to_element: AElement
        return self.relation_type, self.from_parent, self.from_element, \
            self.to_parent, self.to_element 

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

# TODO: 这个最好放在Output中实现。
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
    

class UMLModel(Model):
    # UML的model。
    def __init__(self):
        super(UMLModel, self).__init__()

    def show(self, cmdPkg):
        logging.debug("show diagram of model.")
        
        diagram_type = cmdPkg.diagram
        
        if diagram_type in ( "class", "component"): 
            travel = TravelElements()
        elif diagram_type in ("sequence", "seq"):
            travel = ShowSequence()
        else:
            travel = TravelElements()

        travel.travel(self.elements.values())
        travel.finish()
    
    def create_uml_class(self, cmdPkg):
        e = UMLClass(cmdPkg.name, cmdPkg.no, cmdPkg.title, cmdPkg.color)
        if self.add_element(cmdPkg.name, e):
            return Return.ERROR
        else:
            return Return.OK
    
    def create_uml_component(self, cmdPkg):
    
        e = UMLComponent(cmdPkg.name, cmdPkg.no, cmdPkg.title, cmdPkg.color)
        if self.add_element(cmdPkg.name, e):
            return Return.ERROR
        else:
            return Return.OK
        
    def uml_class_add_field(self, cmdPkg):
    
        e = self.find_element(cmdPkg.target)
        e = e.add_field(cmdPkg.name, cmdPkg.type)

        return Return.OK
    
    def uml_class_add_method(self, cmdPkg):
    
        # find class or component
        e = self.find_element(cmdPkg.target)
        
        # create a new Method element.
        m = UMLMethod(cmdPkg.name, cmdPkg.no, cmdPkg.name, e)
        if self.add_element(cmdPkg.name, m):
            return Return.OK
        else:
            return Return.ERROR
        
        e = e.add_method(m)

        return Return.OK

    def uml_class_relation_set_relation(self, cmdPkg):
    
        e = self.find_element(cmdPkg.target)
        from_e = self.find_element(cmdPkg.from_e)
        to_e = self.find_element(cmdPkg.to)
        e = e.set_relation(cmdPkg.name, from_e, to_e)

        return Return.OK
    
    def uml_add_relation(self, cmdPkg):
            
        from_e = self.find_element(cmdPkg.from_e)
        to_e = self.find_element(cmdPkg.to)
        
        if from_e is None or to_e is None:
            return False
    
        if isinstance(from_e, UMLClass):
            name = AGlobalName.get_unique_name("ClassRelation")
            r = UMLClassRelation(name, cmdPkg.no)
        elif isinstance(from_e, UMLComponent):
            name = AGlobalName.get_unique_name("ComponentRelation")
            r = UMLComponentRelation(name, cmdPkg.no)

        if self.add_element(name, r):
            return Return.ERROR
        
        r.set_relation(cmdPkg.type, cmdPkg.title, from_e, to_e)

        return Return.OK
    
    def uml_add_invoke(self, cmdPkg):
        
        # 找到必须有的选项，和对应的对象。
        from_parent_e = None
        if cmdPkg.from_parent != None:
            from_parent_e = self.find_element(cmdPkg.from_parent)
        
        if from_parent_e is None:
            return False
        
        from_e = None
        if cmdPkg.from_e is not None:
            from_e = self.find_element(cmdPkg.from_e)
        
        if from_e is None:
            return False
        
        to_parent_e = None
        if cmdPkg.to_parent != None:
            to_parent_e = self.find_element(cmdPkg.to_parent)
        
        if to_parent_e is None:
            return False
        
        to_e = None
        if cmdPkg.to is not None:
            to_e = self.find_element(cmdPkg.to)
            
        if to_e is None:
            return False
        
        # 将方法和类、组件联系在一起。
        #rm = UMLElement2MethodRelation("Have", "have", _e, m)
        #if self.add_element(m.name, rm):
        #    return Return.ERROR
    
        # 添加 两个方法之间的关系。
        #name = AGlobalName.get_unique_name(to_parent_e)
        # TODO 名字不好起，在代码中是一个函数调用另外一个函数。
        name = "%s->%s" % (cmdPkg.from_e, cmdPkg.to)
        r = UMLMethodRelation(name, cmdPkg.no)
        r.set_relation("Use", from_parent_e, from_e, to_parent_e, to_e)
        
        if not self.add_element(r.name, r):
            return Return.ERROR

        return Return.OK
        