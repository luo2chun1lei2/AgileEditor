# -*- coding:utf-8 -*-
# 控制所有的模块，以及单独的模块。
# 1. 接受外部的操控，包括命令输入、鼠标输入等。
# 2. 控制所有的模块，以及各个子模块。
# 3. Control不需要知道每个模块的具体含义。

from Model import *
from Return import *

def program_usage():
    # 和 PROGRAM_CMD 一致
    print 'program usage:'
    print 'help: show help information.'
    print 'script <script file path>: run input script'

def control_usage():
    # 和 CMDLINE_CMD 一致。
    print 'control usage:'
    print 'help: show help information.'
    print 'quit: quit from control.'
    print 'test: test this program.'
    print 'select: select on element and do something to it.'
    print 'insert: insert element.'
    print 'update: update properties of element.'
    print 'delete: delete element or relation.'
    print 'drop: drop all data.'
    

# TODO 目前还用不到。
class SystemCommand(object):
    # 系统级别的命令。
    # 命令是解析好的“描述如何执行的数据”，和普通的命令相比，不适用于人类阅读的，而是用于方便执行的。
    def __self__(self):
        super(SystemCommand, self).__init__()

class Control(object):
    
    def __init__(self, model):
        # model: Model: control对应的模型
        super(Control, self).__init__()
        self.model = model
    
    def do(self, str_action):
        # 执行action
        # str_action: Action: 做的动作，以字符串格式
        # return：bool：无法处理这个命令。
        
        if str_action.startswith("#"):
            logging.debug('One comment: %s.' % str_action)
            return Return.OK

        argv = str_action.split()
        if len(argv) == 0:
            logging.debug('One empty line: %s.' % str_action)
            return Return.OK
        
        if argv[0] == "help":
            self._help()
        elif argv[0] == "show":
            self._show()
            
        elif argv[0] == "UMLClass":
            # ex: UMLClass --id=e1 --name="ServiceProviderBridge"
            opts, args = self._parse_one_action(argv[1:], "", ["id=", "name="])
            if not opts is None:
                self._create_uml_class(opts, args)
                
        elif argv[0] == "UMLClassRelation":
            # ex: UMLClassRelation --id=r1 --name='backing_dir'
            opts, args = self._parse_one_action(argv[1:], "", ["id=", "name="])
            if not opts is None:
                self._create_uml_class_relation(opts, args)
            
        elif argv[0] == "add_field":
            # ex: add_field --target_id=e1 --name="backing_dir" --type="zx:channel"
            opts, args = self._parse_one_action(argv[1:], "",
                            ["target_id=", "name=", "type="])
            if not opts is None:
                self._uml_class_add_field(opts, args)
            
        elif argv[0] == "set_relation":
            # ex: set_relation --target_id=r1 --name='Composition' --from=e1 --to=e3
            opts, args = self._parse_one_action(argv[1:], "",
                            ["target_id=", "name=", "from=", "to="])
            if not opts is None:
                self._uml_class_relation_set_relation(opts, args)
                
        
        else: 
            print "Unknown MVC command:%s" % argv[0]
            self._help()
            return Return.ERROR
        
        # 目前Control无法退出程序，只能执行命令。
        return Return.OK

    def _help(self):
        print 'mvc usage:'
        print 'help: show help information.'
        print 'script -l <path>: load script.'

    def _parse_one_action(self, argv, short_args, long_args):
        try:
            opts, args = getopt.getopt(argv, short_args, long_args)
        except getopt.GetoptError, err:
            print str(err)
            self._help()
            return (None, None)
        
        return (opts, args)
    
    def _show(self):
        logging.debug("show diagram of model.")
        
        travel = TravelElements()
        travel.travel(self.model.elements.values())
        travel.finish()
    
    def _create_uml_class(self, opts, args):
        opt_id = None
        opt_name = None
        for o, a in opts:
            if o in ('--id'):
                opt_id = a
            elif o in ('--name'):
                opt_name = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = UMLClass(opt_name)
        self.model.add_element(opt_id, e)
        return Return.OK
    
    def _create_uml_class_relation(self, opts, args):
        opt_id = None
        opt_name = None
        for o, a in opts:
            if o in ('--id'):
                opt_id = a
            elif o in ('--name'):
                opt_name = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = UMLClassRelation(opt_name)
        self.model.add_element(opt_id, e)
        return Return.OK
    
    def _uml_class_add_field(self, opts, args):
        opt_name = None
        opt_target = None
        opt_type = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            elif o in ('--target_id'):
                opt_target = a
            elif o in ('--type'):
                opt_type = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = self.model.find_element(opt_target)
        e = e.add_field(opt_name, opt_type)

        return Return.OK
    
    def _uml_class_relation_set_relation(self, opts, args):
        opt_name = None
        opt_target = None
        opt_from = None
        opt_to = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            elif o in ('--target_id'):
                opt_target = a
            elif o in ('--from'):
                opt_from = a
            elif o in ('--to'):
                opt_to = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = self.model.find_element(opt_target)
        from_e = self.model.find_element(opt_from)
        to_e = self.model.find_element(opt_to)
        e = e.set_relation(opt_name, from_e, to_e)

        return Return.OK
    