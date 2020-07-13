# -*- coding:utf-8 -*-
# 控制所有的模块，以及单独的模块。
# 1. 接受外部的操控，包括命令输入、鼠标输入等。
# 2. 控制所有的模块，以及各个子模块。
# 3. Control不需要知道每个模块的具体含义。

from mvc.Model import *
from misc.Return import *
from misc.Utils import *

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
        self.no = 0
    
    def do(self, str_action):
        # 执行action
        # str_action: Action: 做的动作，以字符串格式
        # return：bool：无法处理这个命令。
        
        self.no = self.no + 1
        
        if str_action.startswith("#"):
            logging.debug('One comment: %s.' % str_action)
            return Return.OK

        # TODO 不能用这个函数，因为会将“xxx xxx”的字符串也分割。
        argv = util_split_command_args(str_action)
        if len(argv) == 0:
            logging.debug('One empty line: %s.' % str_action)
            return Return.OK
        
        if argv[0] == "help":
            self._help()
        elif argv[0] == "show":
            # ex: show sequence/class/component
            # Default is class. class = component. only one.
            
            opts, args = self._parse_one_action(argv[1:], "", [""])
            if args is None or len(args) == 0:
                diagram = "class"
            else:
                diagram = args[len(args) - 1]
                
            self._show(diagram)

        elif argv[0] == "UMLClass":
            # 类型。
            # ex: UMLClass --name=ServiceProviderBridge --title=ServiceProviderBridge --color=Yellow
            # 如果title是空的，那么title就是name。
            opts, args = self._parse_one_action(argv[1:], "", ["name=", "title=", "color="])
            if not opts is None:
                self._create_uml_class(self.no, opts, args)
            
        elif argv[0] == "UMLComponent":
            # 组件。
            # ex: UMLComponent --name="Android Proxy" --color=Yellow
            opts, args = self._parse_one_action(argv[1:], "", ["name=", "title=", "color="])
            if not opts is None:
                self._create_uml_component(self.no, opts, args)
                
        elif argv[0] == "add_field":
            # 类对象中，添加一个“字段”。
            # ex: add_field --target=abc --name=backing_dir --type=zx:channel
            opts, args = self._parse_one_action(argv[1:], "",
                            ["target=", "name=", "type="])
            if not opts is None:
                self._uml_class_add_field(self.no, opts, args)

        elif argv[0] == "add_method":
            # 类对象中添加一个函数。
            # ex: add_method --name=foo --targe=file
            # 在target的模块中，添加一个方法，名字是 name。
            opts, args = self._parse_one_action(argv[1:], "",
                            ["name=", "target="])
            if not opts is None:
                self._uml_class_add_method(self.no, opts, args)
                
        elif argv[0] == "add_relation":
            # 两个对象之间的关系。
            # ex: add_relation --title="get/send msg" --type=Composition \
            #        --from="Android Proxy" --to="Android ipc"
            opts, args = self._parse_one_action(argv[1:], "",
                            ["title=", "type=", "from=", "to="])
            if not opts is None:
                self._uml_add_relation(self.no, opts, args)
                
        elif argv[0] == "add_invoke":
            # 函数之间的调用关系。
            # ex: add_invoke --from_parent=client_tipc --from=xxx --to_parent=file --to=file_get_block
            # 允许 from 可以为空。parent代表method所在的模块，因为method允许在一定范围内可见和隐藏，就存在重名问题。
            opts, args = self._parse_one_action(argv[1:], "",
                            ["from_parent=", "from=", "to_parent=", "to="])
            
            if not opts is None:
                self._uml_add_invoke(self.no, opts, args)
        
        else: 
            print ("Unknown MVC command:%s" % argv[0])
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
    
    def _show(self, diagram_type=None):
        logging.debug("show diagram of model.")
        
        if diagram_type in ( "class", "component"): 
            travel = TravelElements()
        elif diagram_type in ("sequence", "seq"):
            travel = ShowSequence()
        else:
            travel = TravelElements()

        travel.travel(self.model.elements.values())
        travel.finish()
    
    def _create_uml_class(self, no, opts, args):
        opt_name = None
        opt_title = None
        opt_color = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            elif o in ('--title'):
                opt_title = a
            elif o in ('--color'):
                opt_color = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = UMLClass(opt_name, no, opt_title, opt_color)
        if self.model.add_element(opt_name, e):
            return Return.ERROR
        else:
            return Return.OK
    
    def _create_uml_component(self, no, opts, args):
        opt_name = None
        opt_title = None
        opt_color = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            elif o in ('--title'):
                opt_title = a
            elif o in ('--color'):
                opt_color = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = UMLComponent(opt_name, no, opt_title, opt_color)
        if self.model.add_element(opt_name, e):
            return Return.ERROR
        else:
            return Return.OK
    
    # TODO: useless, can remove
    def _create_uml_class_relation(self, no, opts, args):
        opt_name = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = UMLClassRelation(opt_name, no)
        if self.model.add_element(opt_name, e):
            return Return.OK
        else:
            return Return.ERROR
    
    def _uml_class_add_field(self, no, opts, args):
        opt_name = None
        opt_target = None
        opt_type = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            elif o in ('--target'):
                opt_target = a
            elif o in ('--type'):
                opt_type = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
    
        e = self.model.find_element(opt_target)
        e = e.add_field(opt_name, opt_type)

        return Return.OK
    
    def _uml_class_add_method(self, no, opts, args):
        opt_name = None
        opt_target = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            elif o in ('--target'):
                opt_target = a
            else:
                print ('Find unknown option:%s' % (o))
                return Return.ERROR
    
        # find class or component
        e = self.model.find_element(opt_target)
        
        # create a new Method element.
        m = UMLMethod(opt_name, no, opt_name, e)
        if self.model.add_element(opt_name, m):
            return Return.OK
        else:
            return Return.ERROR
        
        e = e.add_method(m)

        return Return.OK

    def _uml_class_relation_set_relation(self, no, opts, args):
        opt_name = None
        opt_target = None
        opt_from = None
        opt_to = None
        for o, a in opts:
            if o in ('--name'):
                opt_name = a
            elif o in ('--target'):
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
    
    def _uml_add_relation(self, no, opts, args):
        opt_title = None
        opt_type = None
        opt_from = None
        opt_to = None
        for o, a in opts:
            if o in ('--title'):
                opt_title = a
            elif o in ('--type'):
                opt_type = a
            elif o in ('--from'):
                opt_from = a
            elif o in ('--to'):
                opt_to = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
            
        from_e = self.model.find_element(opt_from)
        to_e = self.model.find_element(opt_to)
        
        if from_e is None or to_e is None:
            return False
    
        if isinstance(from_e, UMLClass):
            name = AGlobalName.get_unique_name("ClassRelation")
            r = UMLClassRelation(name, no)
        elif isinstance(from_e, UMLComponent):
            name = AGlobalName.get_unique_name("ComponentRelation")
            r = UMLComponentRelation(name, no)

        if self.model.add_element(name, r):
            return Return.ERROR
        
        r.set_relation(opt_type, opt_title, from_e, to_e)

        return Return.OK
    
    def _uml_add_invoke(self, no, opts, args):
        # 只添加 to 到 to_parent 中，from应该已经存在。
        opt_from_parent = None
        opt_from = None
        opt_to_parent = None
        opt_to = None
        # 注意下面的顺序，字符少的在上面，字符多且包括上面字符的，在下面。
        for o, a in opts:
            if o in ('--from'):
                opt_from = a
            elif o in ('--from_parent'):
                opt_from_parent = a
            elif o in ('--to'):
                opt_to = a
            elif o in ('--to_parent'):
                opt_to_parent = a
            else:
                print 'Find unknown option:%s' % (o)
                return Return.ERROR
        
        # 找到必须有的选项，和对应的对象。
        from_parent_e = None
        if opt_from_parent != None:
            from_parent_e = self.model.find_element(opt_from_parent)
        
        if from_parent_e is None:
            return False
        
        from_e = None
        if opt_from is not None:
            from_e = self.model.find_element(opt_from)
        
        if from_e is None:
            return False
        
        to_parent_e = None
        if opt_to_parent != None:
            to_parent_e = self.model.find_element(opt_to_parent)
        
        if to_parent_e is None:
            return False
        
        to_e = None
        if opt_to is not None:
            to_e = self.model.find_element(opt_to)
            
        if to_e is None:
            return False
        
        # 将方法和类、组件联系在一起。
        #rm = UMLElement2MethodRelation("Have", "have", _e, m)
        #if self.model.add_element(m.name, rm):
        #    return Return.ERROR
    
        # 添加 两个方法之间的关系。
        #name = AGlobalName.get_unique_name(to_parent_e)
        # TODO 名字不好起，在代码中是一个函数调用另外一个函数。
        name = "%s->%s" % (opt_from, opt_to)
        r = UMLMethodRelation(name, no)
        r.set_relation("Use", from_parent_e, from_e, to_parent_e, to_e)
        
        if not self.model.add_element(r.name, r):
            return Return.ERROR

        return Return.OK
    