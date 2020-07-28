# -*- coding:utf-8 -*-

# 作为测试程序的一个Model，从Model继承下来。
# 内部有固定代码实现的测试模型。
from model.Model import *

class TestModel1(Model):
    def __init__(self):
        super(TestModel1, self).__init__()

    def test_db(self):
        test_db()
    
    def test1(self):
        # TODO: 应该删除！
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