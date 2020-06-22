# -*- coding:utf-8 -*-

# TODO 以后将简单的全局名字系统，修改成“名字空间”, NameSpace
# 名字空间管理，给每个对象一个唯一的名字路径，保证不会出现名字冲突。
# 0. 名字只能是 "[0-9][a-z][A-Z][_-\ \.]"。 
# 1. 所有的名字都形成一个树（或者森林？），名字路径(name path)是对应名字的唯一且有效的查找路径。
#    例子： a/bc/123
# 2. 每个名字都可以有一个 object。
# 3. 当名字超出范围后，就进行消除。
# 4. 每个名字注册时，都需要提交自己的名字，和自己所在的名字空间(category)的名字。

import os, re

class AGlobalName(object):
    
    # 管理所有元素的名字，不能有重复！
    # 是单例模式。
    # TODO: 这个太简单，需要构造“树”。
    categories = {}
    
    def __init__(self):
        super(AGlobalName, self).__init__()
       
    @staticmethod 
    def is_valid(self, name):
        # 检查名字是否符合要求
        # @param name: string: 要验证的名字
        # @return boolean: true is OK.
        return re.search('^[0-9][a-z][A-Z][_\-\ \.]+$', name)
    
    @staticmethod
    def check_name(category, name):
        # @param category: string: 对象所在的种类
        # @param name: string: 需要注册的名字
        # @return False:有重复的名字，True:可以注册
        if not category in AGlobalName.categories:
            return True
    
        if name in AGlobalName.categories[category]:
            return False
        
        return True
    
    @staticmethod
    def get_unique_name(category):
        # 得到一个category的随机名字。
        while True:
            name = os.tmpnam()
            if AGlobalName.check_name(category, name):
                return name
    
    @staticmethod
    def register(category, name):
        # @param category: string: name 所在的命名空间名字。
        # @param name : string : 需要注册的名字
        # @return False:有重复的名字，True:注册成功。
        
        if not category in AGlobalName.categories:
            AGlobalName.categories[category] = [name]
            return True
        
        if not name in AGlobalName.categories[category]:
            AGlobalName.categories[category].append(name)
            return True

        print '"%s/%s" is in global names.' % (category, name)
        return False
    
    @staticmethod
    def unregister(category, name):
        # @param name:string: 需要反注册的名字
        # 不用返回情况，因为无论如何都要被删除。
        if category in AGlobalName.categories:
            if name in AGlobalName.categories[category]:
                AGlobalName.categories[category].remove(name)
                if len(AGlobalName.categories[category]) == 0:
                    del AGlobalName.categories[category]
    
class EnableGlobalName(object):
    # 继承了这个类的类，就将要求注册全局的名字。
    
    def __init__(self, category, name):
        # @param category: string: 
        super(EnableGlobalName, self).__init__()
        
        rlt = AGlobalName.register(category, name)
        if not rlt:
            print "Cannot create the element with category=\"%s\", name=\"%s\"." % (category, name)
            raise ValueError("Category(%s) and Name(%s) is duplicated." % (category, name))
    
        self.category = category
        self.name = name
    
    def __del__(self):
        AGlobalName.unregister(self.category, self.name)