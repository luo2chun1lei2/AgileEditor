# -*- coding:utf-8 -*-

# 针对Model的Executor。

import logging, getopt

from model import *
from model.concrete.ModelUML import *
from misc.Return import *
from misc.Utils import *
from parser.CommandPackage import *

class ExecutorModelUML(object):
    # 执行针对Model的command package
    
    def __init__(self, model, output):
        super(ExecutorModelUML, self).__init__()
        self.model = model
        self.output = output
        self.no = 0
        
    def execute(self, cmdPkg):
        
        if cmdPkg.cmdId == CommandId.MODEL_SHOW:
            # 为了显示，就需要 Model和Output配合。
            self.output.show(self.model, cmdPkg)

        elif cmdPkg.cmdId == CommandId.MODEL_UMLCLASS:
            # 类型。
            # ex: UMLClass --name=ServiceProviderBridge --title=ServiceProviderBridge --color=Yellow
            # 如果title是空的，那么title就是name。
            self.model.create_uml_class(cmdPkg)
            
        elif cmdPkg.cmdId == CommandId.MODEL_UML_COMPONENT:
            # 组件。
            # ex: UMLComponent --name="Android Proxy" --color=Yellow
            self.model.create_uml_component(cmdPkg)
                
        elif cmdPkg.cmdId == CommandId.MODEL_ADD_FIELD:
            # 类对象中，添加一个“字段”。
            # ex: add_field --target=abc --name=backing_dir --type=zx:channel
            self.model.uml_class_add_field(cmdPkg)

        elif cmdPkg.cmdId == CommandId.MODEL_ADD_METHOD:
            # 类对象中添加一个函数。
            # ex: add_method --name=foo --targe=file
            # 在target的模块中，添加一个方法，名字是 name。
            self.model.uml_class_add_method(cmdPkg)
                
        elif cmdPkg.cmdId == CommandId.MODEL_ADD_RELATION:
            # 两个对象之间的关系。
            # ex: add_relation --title="get/send msg" --type=Composition \
            #        --from="Android Proxy" --to="Android ipc"
            self.model.uml_add_relation(cmdPkg)
                
        elif cmdPkg.cmdId == CommandId.MODEL_ADD_INVOKE:
            # 函数之间的调用关系。
            # ex: add_invoke --from_parent=client_tipc --from=xxx --to_parent=file --to=file_get_block
            # 允许 from 可以为空。parent代表method所在的模块，因为method允许在一定范围内可见和隐藏，就存在重名问题。
            self.model.uml_add_invoke(cmdPkg)
        
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
    

