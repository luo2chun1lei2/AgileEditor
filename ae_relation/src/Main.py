#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt, shutil
from Element import *
from PlantUML import *
from Utils import *
from Storage import *
    
class UMLClass(AElement):
    # UML's class
    def __init__(self, name):
        super(UMLClass, self).__init__(name)
        self.fields = []

    def add_field(self, field_name, field_type):
        self.fields.append((field_name, field_type))

class UMLClassRelation(ARelation):
    # 类和类之间的关系
    def __init__(self, name):
        super(UMLClassRelation, self).__init__(name)

    def set_relation(self, relation_type, from_element, to_element):    # TODO 此处参数是否应该不定个数?
        # @param from_element:AElement:
        # @param to_element:AElement:
        # @param relation_type:string: Extension/Composition/Aggregation
        self.from_element = from_element
        self.to_element = to_element
        self.relation_type = relation_type
    
    def get_relation(self):
        return self.relation_type, self.from_element, self.to_element 
        
class TravelElements(object):
    # Travel Elements to create some thing
    # use planuml to create diagram
    
    def __init__(self):
        self.uml = PlantUML("../plantuml/plantuml.jar")
        self.data_fd, self.data_path = Utils.create_tmpfile("txt")
        
        self._write("@startuml")
    
    def _write(self, str):
        # 会在字符串后面加入空格。
        os.write(self.data_fd, "%s\n" % str)
    
    def travel(self, elements):
        # @param elements: AElement[]: set of all needed elements.
        # @return bool: True is ok, False is failed.
        
        for e in elements:
            if isinstance(e, UMLClassRelation):
                type, from_element, to_element = e.get_relation()
                if type is 'Extension': # TODO: 继承不需要额外的名字。
                    self._write("%s --|> %s : %s" % (from_element.name, to_element.name, e.name))
                elif type is 'Composition':
                    self._write("%s *-- %s : %s" % (from_element.name, to_element.name, e.name))
                elif type is 'Aggregation':
                    self._write("%s o-- %s : %s" % (from_element.name, to_element.name, e.name))
                else:
                    print "Don't recognize this type\"\" of class relation" % type
                    sys.exit(1)
            elif isinstance(e, UMLClass):
                self._write("class %s {" % e.name)
                for field_name, field_type in e.fields:
                    self._write("%s : %s" % (field_name, field_type))
                self._write("}")
                
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

def test():
    test_db()

def test2():
    try:
        # set elements.
        e1 = UMLClass('ServiceProviderBridge')
        e1.add_field("backing_dir", "zx:channel")
        e1.add_field("backend", "ServiceProviderPtr")
        e2 = UMLClass('ServiceProvider')
        e3 = UMLClass('zx::channel')
        e4 = UMLClass('ServiceProviderPtr')
        
        r1 = UMLClassRelation('backing_dir')
        r1.set_relation('Composition', e1, e3)
        r2 = UMLClassRelation('backend')
        r2.set_relation('Composition', e1, e4)
        r3 = UMLClassRelation('None')
        r3.set_relation('Extension', e1, e2)
        
        elements = [e1, e2, e3, e4, r1, r2, r3]
        
        travel = TravelElements()
        travel.travel(elements)
        travel.finish()
    except Exception, ex:
        print ex.message
    

#######################################
## Entry of program.

def usage():
    print 'program usage:'
    print '-h, --help: show help information.'

def main(argv):
    u''' Analysis command's arguments '''
    
    # analysis code.
    try:
        opts, args = getopt.getopt(argv[1:], 'h', ['help'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)
    
    test2()
    
    sys.exit(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')
    
    main(sys.argv)
