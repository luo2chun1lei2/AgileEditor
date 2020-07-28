# -*- coding:utf-8 -*-

# 针对Model的Executor。

from model import *
from model.concrete.UMLModel import *
from misc.Return import *
from misc.Utils import *
from parser.CommandPackage import *

import logging
import getopt


class ExecutorModel(object):
    # 执行针对Model的command package
    
    def __init__(self, model):
        super(ExecutorModel, self).__init__()
        self.model = model
        self.no = 0
        
    def execute(self, cmdPkg):
        
        if cmdPkg.cmdId == CommandId.SHOW_HELP:
            self.show_help()    # TODO 显示谁的帮助？
        elif cmdPkg.cmdId == CommandId.MODEL_SHOW:
            self._show(cmdPkg)

        elif cmdPkg.cmdId == CommandId.MODEL_UMLCLASS:
            # 类型。
            # ex: UMLClass --name=ServiceProviderBridge --title=ServiceProviderBridge --color=Yellow
            # 如果title是空的，那么title就是name。
            self._create_uml_class(cmdPkg)
            
        elif cmdPkg.cmdId == CommandId.MODEL_UML_COMPONENT:
            # 组件。
            # ex: UMLComponent --name="Android Proxy" --color=Yellow
            self._create_uml_component(cmdPkg)
                
        elif cmdPkg.cmdId == CommandId.MODEL_ADD_FIELD:
            # 类对象中，添加一个“字段”。
            # ex: add_field --target=abc --name=backing_dir --type=zx:channel
            self._uml_class_add_field(cmdPkg)

        elif cmdPkg.cmdId == CommandId.MODEL_ADD_METHOD:
            # 类对象中添加一个函数。
            # ex: add_method --name=foo --targe=file
            # 在target的模块中，添加一个方法，名字是 name。
            self._uml_class_add_method(cmdPkg)
                
        elif cmdPkg.cmdId == CommandId.MODEL_ADD_RELATION:
            # 两个对象之间的关系。
            # ex: add_relation --title="get/send msg" --type=Composition \
            #        --from="Android Proxy" --to="Android ipc"
            self._uml_add_relation(cmdPkg)
                
        elif cmdPkg.cmdId == CommandId.MODEL_ADD_INVOKE:
            # 函数之间的调用关系。
            # ex: add_invoke --from_parent=client_tipc --from=xxx --to_parent=file --to=file_get_block
            # 允许 from 可以为空。parent代表method所在的模块，因为method允许在一定范围内可见和隐藏，就存在重名问题。
            self._uml_add_invoke(cmdPkg)
        
        else: 
#             logging.error ("Unknown MVC command:%d" % cmdPkg.cmdId)
#             self.show_help()
#             return Return.ERROR
            return Return.UNKNOWN
        
        # TODO: 目前Control无法退出程序，只能执行命令。
        return Return.OK

    def show_help(self):
        print 'command:'
        print 'help: show help information.'
        print 'script -l <path>: load script.'

    def _parse_one_action(self, argv, short_args, long_args):
        try:
            opts, args = getopt.getopt(argv, short_args, long_args)
        except getopt.GetoptError, err:
            print str(err)
            self.show_help()
            return (None, None)
        
        return (opts, args)
    
    def _show(self, cmdPkg):
        logging.debug("show diagram of model.")
        
        diagram_type = cmdPkg.diagram
        
        if diagram_type in ( "class", "component"): 
            travel = TravelElements()
        elif diagram_type in ("sequence", "seq"):
            travel = ShowSequence()
        else:
            travel = TravelElements()

        travel.travel(self.model.elements.values())
        travel.finish()
    
    def _create_uml_class(self, cmdPkg):
        e = UMLClass(cmdPkg.name, cmdPkg.no, cmdPkg.title, cmdPkg.color)
        if self.model.add_element(cmdPkg.name, e):
            return Return.ERROR
        else:
            return Return.OK
    
    def _create_uml_component(self, cmdPkg):
    
        e = UMLComponent(cmdPkg.name, cmdPkg.no, cmdPkg.title, cmdPkg.color)
        if self.model.add_element(cmdPkg.name, e):
            return Return.ERROR
        else:
            return Return.OK
        
    def _uml_class_add_field(self, cmdPkg):
    
        e = self.model.find_element(cmdPkg.target)
        e = e.add_field(cmdPkg.name, cmdPkg.type)

        return Return.OK
    
    def _uml_class_add_method(self, cmdPkg):
    
        # find class or component
        e = self.model.find_element(cmdPkg.target)
        
        # create a new Method element.
        m = UMLMethod(cmdPkg.name, cmdPkg.no, cmdPkg.name, e)
        if self.model.add_element(cmdPkg.name, m):
            return Return.OK
        else:
            return Return.ERROR
        
        e = e.add_method(m)

        return Return.OK

    def _uml_class_relation_set_relation(self, cmdPkg):
    
        e = self.model.find_element(cmdPkg.target)
        from_e = self.model.find_element(cmdPkg.from_e)
        to_e = self.model.find_element(cmdPkg.to)
        e = e.set_relation(cmdPkg.name, from_e, to_e)

        return Return.OK
    
    def _uml_add_relation(self, cmdPkg):
            
        from_e = self.model.find_element(cmdPkg.from_e)
        to_e = self.model.find_element(cmdPkg.to)
        
        if from_e is None or to_e is None:
            return False
    
        if isinstance(from_e, UMLClass):
            name = AGlobalName.get_unique_name("ClassRelation")
            r = UMLClassRelation(name, cmdPkg.no)
        elif isinstance(from_e, UMLComponent):
            name = AGlobalName.get_unique_name("ComponentRelation")
            r = UMLComponentRelation(name, cmdPkg.no)

        if self.model.add_element(name, r):
            return Return.ERROR
        
        r.set_relation(cmdPkg.type, cmdPkg.title, from_e, to_e)

        return Return.OK
    
    def _uml_add_invoke(self, cmdPkg):
        
        # 找到必须有的选项，和对应的对象。
        from_parent_e = None
        if cmdPkg.from_parent != None:
            from_parent_e = self.model.find_element(cmdPkg.from_parent)
        
        if from_parent_e is None:
            return False
        
        from_e = None
        if cmdPkg.from_e is not None:
            from_e = self.model.find_element(cmdPkg.from_e)
        
        if from_e is None:
            return False
        
        to_parent_e = None
        if cmdPkg.to_parent != None:
            to_parent_e = self.model.find_element(cmdPkg.to_parent)
        
        if to_parent_e is None:
            return False
        
        to_e = None
        if cmdPkg.to is not None:
            to_e = self.model.find_element(cmdPkg.to)
            
        if to_e is None:
            return False
        
        # 将方法和类、组件联系在一起。
        #rm = UMLElement2MethodRelation("Have", "have", _e, m)
        #if self.model.add_element(m.name, rm):
        #    return Return.ERROR
    
        # 添加 两个方法之间的关系。
        #name = AGlobalName.get_unique_name(to_parent_e)
        # TODO 名字不好起，在代码中是一个函数调用另外一个函数。
        name = "%s->%s" % (cmdPkg.from_e, cmdPkg.to)
        r = UMLMethodRelation(name, cmdPkg.no)
        r.set_relation("Use", from_parent_e, from_e, to_parent_e, to_e)
        
        if not self.model.add_element(r.name, r):
            return Return.ERROR

        return Return.OK
