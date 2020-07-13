#-*- coding:utf-8 -*-

# Parser模块：
# 1. 标准的命令包

class CommandId():
    SET_LOG_LEVEL = 0
    SHOW_HELP = 1
    QUIT = 2
    EXECUTE_SCRIPT = 3
    ENTER_INTERVIEW = 4
    MODEL_NAME = 5

class CommandPackage(object):
    # 只保存标准的数据包，
    # 1. 要支持序列化
    # 2. 要可以嵌套包含，形成命令列表
    
    def __init__(self, cmdId):
        super(CommandPackage, self).__init__()
        self.cmdId = cmdId
        
class CommandPackageList(object):
    # 保存CommandPackage的列表

    def __init__(self, cmdPkgs):
        #@param cmdPkgs CommandPackage[]
        super(CommandPackage, self).__init__()
        
        self.cmdPkgs = cmdPkgs
