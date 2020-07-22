# -*- coding:utf-8 -*-

# 分析针对Model的命令。
# 命令格式是 getopt 格式的。

from mvc.Model import *
from misc.Return import *
from misc.Utils import *
from parser.CommandPackage import *

import logging
import getopt

def program_usage():
    # 和 PROGRAM_CMD 一致
    print ('program usage:')
    print ('help: show help information.')
    print ('script <script file path>: run pipe script')

def control_usage():
    # 和 CMDLINE_CMD 一致。
    print ('control usage:')
    print ('help: show help information.')
    print ('quit: quit from control.')
    print ('test: test this program.')
    print ('select: select on element and do something to it.')
    print ('insert: insert element.')
    print ('update: update properties of element.')
    print ('delete: delete element or relation.')
    print ('drop: drop all data.')

class ParserCommandLine(object):
    # 这个parser能够分析类似命令行的脚本。就是用getopt可以分析的命令行。
    
    def __init__(self, model):
        super(ParserCommandLine, self).__init__()
        self.model = model
        self.no = 0
    
    def parse(self, line_no, line):
        # 分析输入。
        # @param line_no int 行号
        # @param line string 做的动作，以字符串格式
        # @param return CommandPackage[]
    
        cmdPkgs = []
        self.no = self.no + 1
        
        if line.startswith("#"):
            # 是注释，什么都不用做。
            logging.debug('One comment: %s.' % line)
            return cmdPkgs

        # TODO 不能用这个函数，因为会将“xxx xxx”的字符串也分割。
        argv = util_split_command_args(line)
        if len(argv) == 0:
            logging.debug('One empty line: %s.' % line)
            return cmdPkgs
        
        if argv[0] == "help":
            cmdPkg = CommandPackage(CommandId.SHOW_HELP)
            
        elif argv[0] == "show":
            # ex: show sequence/class/component
            # Default is class. class = component. only one.
            
            cmdPkg = CommandPackage(CommandId.MODEL_SHOW)
            
            args = self._parse_one_action_and_setattr(argv[1:], "", [], cmdPkg, [])
            if args is None or len(args) == 0:
                cmdPkg.diagram = "class"
            else:
                cmdPkg.diagram = args[len(args) - 1]

        elif argv[0] == "UMLClass":
            # 类型。
            # ex: UMLClass --name=ServiceProviderBridge --title=ServiceProviderBridge --color=Yellow
            # 如果title是空的，那么title就是name。
            
            cmdPkg = CommandPackage(CommandId.MODEL_UMLCLASS)
            self._parse_one_action_and_setattr(argv[1:], "", ["name=", "title=", "color="],
                                                  cmdPkg, ["name", "title", "color"])

        elif argv[0] == "UMLComponent":
            # 组件。
            # ex: UMLComponent --name="Android Proxy" --color=Yellow
            
            cmdPkg = CommandPackage(CommandId.MODEL_UML_COMPONENT)
            self._parse_one_action_and_setattr(argv[1:], "", ["name=", "title=", "color="],
                                                  cmdPkg, ["name", "title", "color"])
                
        elif argv[0] == "add_field":
            # 类对象中，添加一个“字段”。
            # ex: add_field --target=abc --name=backing_dir --type=zx:channel
            
            cmdPkg = CommandPackage(CommandId.MODEL_ADD_FIELD)
            self._parse_one_action_and_setattr(argv[1:], "", ["target=", "name=", "type="],
                                                  cmdPkg, ["target", "name", "type"])

        elif argv[0] == "add_method":
            # 类对象中添加一个函数。
            # ex: add_method --name=foo --targe=file
            # 在target的模块中，添加一个方法，名字是 name。
            
            cmdPkg = CommandPackage(CommandId.MODEL_ADD_METHOD)
            self._parse_one_action_and_setattr(argv[1:], "", ["name=", "target="],
                                                  cmdPkg, ["name", "target"])
                            
        elif argv[0] == "add_relation":
            # 两个对象之间的关系。
            # ex: add_relation --title="get/send msg" --type=Composition \
            #        --from="Android Proxy" --to="Android ipc"
            
            cmdPkg = CommandPackage(CommandId.MODEL_ADD_RELATION)
            self._parse_one_action_and_setattr(argv[1:], "", ["title=", "type=", "from=", "to="],
                                                  cmdPkg, ["title", "type", "from_e", "to"])
                
        elif argv[0] == "add_invoke":
            # 函数之间的调用关系。
            # ex: add_invoke --from_parent=client_tipc --from=xxx --to_parent=file --to=file_get_block
            # 允许 from 可以为空。parent代表method所在的模块，因为method允许在一定范围内可见和隐藏，就存在重名问题。
            
            cmdPkg = CommandPackage(CommandId.MODEL_ADD_INVOKE)
            self._parse_one_action_and_setattr(argv[1:], "", ["from_parent=", "from=", "to_parent=", "to="],
                                                  cmdPkg, ["from_parent", "from_e", "to_parent", "to"])
        
        else: 
            logging.error ("Unknown MVC command:%s" % argv[0])
            #self.show_help()
            return cmdPkgs
        
        cmdPkg.no = self.no
        cmdPkgs.append(cmdPkg)
        
        return cmdPkgs

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
    
    def _parse_one_action_and_setattr(self, argv, short_args, long_args, instance, attrs):
        # @return args
        
        for attr in attrs:
            setattr(instance, attr, None)
        
        opts, args = self._parse_one_action(argv, short_args, long_args)
        if not opts is None:
            for o, a in opts:
                attr_name = None
                attr_value = None
                for arg in long_args:
                    if o.replace("-", "") == arg.replace("=", ""):
                        index = long_args.index(arg)
                        attr_name = attrs[index]
                        attr_value = a
                        
                        setattr(instance, attr_name, attr_value)
                        break

                if attr_name is None:
                    logging.error('Find unknown option:%s' % (o))

        return args
