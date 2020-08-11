# -*- coding:utf-8 -*-

# Parser：
# 分析基本的Element和Relation的脚本。

from model.Model import *
from misc.Return import *
from misc.Utils import *
from parser.Parser import *
from parser.CommandPackage import *

import logging, getopt

class ParserBasic(Parser):
    # 这个parser能够分析类似命令行的脚本。就是用getopt可以分析的命令行。
    
    def __init__(self, model):
        super(ParserBasic, self).__init__()
        self.model = model
        self.no = 0
        
        self.join_lines = JoinLines()
        
    def parse(self, line_no, line):
        # 分析输入。
        # @param line_no int 行号
        # @param line string 做的动作，以字符串格式
        # @param return CommandPackage[]
        
        line = self.join_lines.join(line_no, line)
        if line == None:
            return []
    
        cmdPkgs = []
        self.no = self.no + 1
        
        if line.startswith("#"):
            # 是注释，什么都不用做。
            logging.debug('One comment: %s.' % line)
            return cmdPkgs

        argv = util_split_command_args(line)
        if len(argv) == 0:
            logging.debug('One empty line: %s.' % line)
            return cmdPkgs
        
        if argv[0] == "help":
            cmdPkg = CommandPackage(CommandId.HELP_PROCESSOR)
            
        elif argv[0] == "show":
            # ex: show sequence/class/component
            # Default is class. class = component. only one.
            
            cmdPkg = CommandPackage(CommandId.MODEL_SHOW)
            
            args = self._parse_one_action_and_setattr(argv[1:], "", [], cmdPkg, [])
            if args is None or len(args) == 0:
                cmdPkg.diagram = "class"
            else:
                cmdPkg.diagram = args[len(args) - 1]

        elif argv[0] == "Element":
            # 类型。
            # ex: Element --name=ServiceProviderBridge --title="xxxx"
            # 如果title是空的，那么title就是name。
            
            cmdPkg = CommandPackage(CommandId.MODEL_ELEMENT)
            self._parse_one_action_and_setattr(argv[1:], "", ["name=", "title=", "type="],
                                                  cmdPkg, ["name", "title", "type"])
                            
        elif argv[0] == "Relation":
            # 两个对象之间的关系。
            # ex: Relation --title="get/send msg" --type="type/depend/own" \
            #        --from="Android Proxy" --to="Android ipc"
            # type : A 是 B 的类型，你是人。
            # depend ： A 依赖 B，比如使用、引用等。
            # own： A 包含 B，比如身体拥有手臂。
            
            cmdPkg = CommandPackage(CommandId.MODEL_RELATION)
            self._parse_one_action_and_setattr(argv[1:], "", ["title=", "type=", "from=", "to="],
                                                  cmdPkg, ["title", "type", "from_e", "to"])

        else: 
            logging.error ("Unknown command:%s" % argv[0])
            return None
        
        cmdPkg.no = self.no
        cmdPkgs.append(cmdPkg)
        
        return cmdPkgs

    def show_help(self):
        print 'Commands for BASIC mode:'
        print '  help : show help information.'
        print '  ... <wait for implementation>.'

    # TODO: 下面两个函数放到util中比较好。
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