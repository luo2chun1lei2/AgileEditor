#-*- coding:utf-8 -*-

# Parser模块：
# 1. 命令包，由Parser产生，然后分发给Executor执行。

class CommandId():
    # Application and processor
    SET_LOG_LEVEL = 1
    # 显示的是此parser自己的help信息。
    SHOW_HELP = 2
    QUIT = 3
    EXECUTE_SCRIPT = 4
    ENTER_INTERVIEW = 5
    LOAD_PROCESSOR = 6
    LOAD_DATA = 7
    QUIT_PROCESSOR = 8
    # 显示的是 processor 的帮助信息，其实是processor内部的所有parser帮助信息。
    HELP_PROCESSOR = 9
    MODEL_SHOW = 10
    
    # Elements of Basic Model
    MODEL_ELEMENT = 30
    MODEL_RELATION = 31
    
    # Elements of UML model.
    MODEL_UMLCLASS = 50
    MODEL_UML_COMPONENT = 51
    MODEL_ADD_FIELD = 52
    MODEL_ADD_METHOD = 53
    MODEL_ADD_RELATION = 54
    MODEL_ADD_INVOKE = 55

class CommandPackage(object):
    # 只保存标准的数据包，
    # 1. 要支持序列化
    # 2. 要可以嵌套包含，形成命令列表
    
    def __init__(self, cmdId):
        super(CommandPackage, self).__init__()
        self.cmdId = cmdId

# TODO:是否有必要？用数组不是就可以了吗？
class CommandPackageList(object):
    # 保存CommandPackage的列表

    def __init__(self, cmdPkgs):
        #@param cmdPkgs CommandPackage[]
        super(CommandPackage, self).__init__()

        self.cmdPkgs = cmdPkgs
