# -*- coding:utf-8 -*-

# 测试UML的Model用的。
# 内部有固定代码实现的测试模型。
from model import *
from model.concrete.ModelUML import *

class ModelUMLTest(unittest.TestCase):

    def test_1(self):
        #test_db()
        pass
    
    def abctest(self):
        # 测试内部的类和函数。
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
            traceback.print_exc()