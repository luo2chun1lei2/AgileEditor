#-*- coding:utf-8 -*-

# 采用如下的方法进行
# 1，每个关系设定用一组符号表示，但是并不是程序
# 2，对应这组符号，编写对应的代码，这里关系对应的不是类型，而是实例，以此减少编程的难度
# 3，将关系设定后，让程序运行，观察结果和总结、提炼程序。
# TODO 关系不正确，如果保存数据，那么应该是每个对象一个，如果只有一个，则不能保存数据，只能用来计算。
import os, sys

# 基础实现不用设定
class ZType(object):
    def __init__(self):
        super(ZType, self).__init__()
        self.properties = {}
        self.relation = {}
    
    def instance(self):
        # 生成子对象
        obj = ZObject()
        
        # 属性的值不能共用
        obj.properties = self.properties.copy()
        for key in obj.properties.keys():
            obj.properties[key] = ZObject()
        
        # 关系可以共用
        obj.relations = self.relations.copy()
        
        return obj
    
    def add_property(self, name):
        self.properties[name] = None
    
    def del_property(self, name):
        self.properties.remove(name)
        
    def add_releation(self, name, relation):
        self.relations[name] = relation
        
    def del_relation(self, name):
        self.relations.remove(name)

class ZAction(ZType):
    def __init__(self):
        super(ZAction, self).__init__()
    
class ZEvent(ZType):
    def __init__(self):
        super(ZEvent, self).__init__()

class ZObject(ZType):
    # 每个对象有一个缺省的类型
    
    def __init__(self):
        super(ZObject, self).__init__()
        self.value = None
        
    def set_value(self, value):
        self.value
        
    def get_value(self):
        return self.value
    
    def set_property(self, name, value):
        if name in self.properties:
            self.properties[name] = value
        else:
            print "Cannot find this property '%s' in object." % (name)
    
    def get_property(self, name):
        if name in self.properties:
            return self.properties[name]
        else:
            print "Cannot find this property '%s' in object." % (name)
            return None

class ZRelation(ZType):
    # 关系是作用在ZObject(类型)之上的，也可以作用在实例上？
    # 关系不能有状态！
    def __init__(self):
        super(ZRelation, self).__init__()
        
# Has extends Relation
class ZHas(ZRelation):
    
    HAS_ONLY_ONE = 1
    HAS_MORE = 2
    HAS_NONE_OR_ONE = 3
    HAS_ANY = 4
    
    # 拥有关系
    def __init__(self):
        super(ZHas, self).__init__()
        self.from_type = ZHas.HAS_ANY
        self.to_type = ZHas.HAS_ONLY_ONE
    
    def set(self, from_obj, from_type, to_obj, to_type):
        from_obj.add_relation(self)
        self.from_type = from_type
        
        to_obj.add_relation(self)
        self.to_type = to_type
    
# 建立School和Student之间的关系
# 本来应该是针对类型设定的，但是Python自动实现比较困难

# -------------------------------------------------
# 使用
def main(argv):
    
    #######################################################
    ## 建立基本的类型和关系
    
    # School extends Object
    # School has property(name)
    School = ZType()
    School.add_property("name")
    
    # Student extends Object
    # Student has property(name) ...
    Student = ZType()
    Student.add_property("name")
    Student.add_property("gender")
    Student.add_property("age")
    
    # School_has_Students extends Has
    # School({0,}students) has student({1}school)
    School_has_Students = ZHas()
    School_has_Students.set(School, "students", ZHas.HAS_ANY,
                            Student, "school", ZHas.HAS_ONLY_ONE)
    
    #######################################################
    ## 开始初始化数据
    
    # school_11 = new School
    # school_11.name = "xxxx"
    school_11 = School.instance()
    school_11.get_property("name").set_value("11中学")
    
    zhang = Student.instance()
    zhang.get_property("name").set_value("张三")
    zhang.get_property("gender").set_value("male")
    zhang.get_property("age").set_value("17")
    
    li = Student.instance()
    li.get_property("name").set_value("李四")
    li.get_property("gender").set_value("female")
    li.get_property("age").set_value("16")
    
    # 关系自动生成students
    school_11.get_relation("students").add(zhang)
    school_11.get_relation("students").add(li)

if __name__ == '__main__':
    '''  主入口  '''
    main(sys.argv)