#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt
from subject_observer import *

def util_print_frame():
    ''' 打印出现错误的位置的上一个调用点，用于调试。
    '''
    import inspect

    stack = inspect.stack()
    frame = stack[2][0]
    if "self" in frame.f_locals:
        the_class = str(frame.f_locals["self"].__module__)
    else:
        the_class = "Unknown"
    the_line = frame.f_lineno
    the_method = frame.f_code.co_name
    print "=-> %s:%d/%s" % (the_class, the_line, the_method)


class VObject(VSubject, VObserver):
    def __init__(self):
        super(VObject, self).__init__()

class VValue(VObject):
    
    def __init__(self, v):
        super(VValue, self).__init__()
        self.value = v
        
    def __str__(self, *args, **kwargs):
        return str(self.value)
    
    def set_value(self, v):
        if self.value == v:
            # 这里制止修改事件“回荡”。
            return
        
        self.value = v
        self.notify_observers()
            
    def get_value(self):
        return self.value
    
class VRelation(VObject):
    # TODO Can method "constrain" be placed here ?
    def __init__(self):
        super(VRelation, self).__init__()
        
class REqualValue(VRelation):
    # value1 is equal with value2.
    # bidirectional
    
    def __init__(self):
        super(REqualValue, self).__init__()
        self.obj1 = None
        self.obj2 = None
        
    def constrain(self, obj1, obj2):
        if not isinstance(obj1, VValue) or not isinstance(obj2, VValue):
            logging.error("obj1 or obj2 is not VValue")
        self.obj1 = obj1
        self.obj2 = obj2
        
        self.obj1.attach_observer(self)
        self.obj2.attach_observer(self)
    
    def _on_subject_update(self, subject):
        ok = False
        if subject is self.obj1:
            ok = True
            self.obj2.set_value(self.obj1.get_value())
                           
        if subject is self.obj2:
            ok = True
            self.obj1.set_value(self.obj2.get_value())
            
        if not ok:
            logging.error("subject is NOT obj1 or obj2.")
        
class VSum(VValue):
    # This is a combined object.
    # value = value1 + value2, 
    # when one of value is changed, then notify observer.
    
    def __init__(self):
        super(VSum, self).__init__(None)    # TODO VValue's init function should be reviewed.
        self.objects = []
        
    def constrain(self, *args):
        
        for arg in args:
            if not isinstance(arg, VValue):
                logging.error("args[%d] is not VValue" % args.index(arg) )
                break
            
            self.objects.append(arg)
            arg.attach_observer(self)
        
    def _on_subject_update(self, subject):
        self.notify_observers()
        
    def set_value(self, value):
        # cannot set value, this is unidirectional.
        # 这里不能设定值，是否应该作为一个属性设置到object中？
        # 这里不实现，不就不会“回荡”了吗？
        #logging.error("This is unidirectional, so cannot set value.")
        pass
        
    def get_value(self):
        sum = 0
        for obj in self.objects:
            sum += obj.get_value()
        return sum
        
def test1():
    obj = VObject()
    rel = VRelation()
    val1 = VValue(100)
    val2 = VValue(99)
    
    equal = REqualValue()
    equal.constrain(val1, val2)
    val1.set_value(1000)
    print val1, val2
    
    val2.set_value(0)
    print val1, val2
    
def test2():
    # v3 = v1 + v2
    v1 = VValue(10)
    v2 = VValue(20)
    v3 = VValue(100)
    
    sum = VSum()
    sum.constrain(v1, v2)
    
    equal = REqualValue()
    equal.constrain(v3, sum)
      
    print v1, v2, v3
      
    v2.set_value(10)
    print v1, v2, v3

#######################################
## Entry of program.

def usage():
    print 'vr usage:'
    print '-h, --help: show help information.'

def main(argv):
    u''' Analysis command's arguments '''
    
    # analysis code.
    try:
        opts, args = getopt.getopt(argv[1:], 'h', ['help'])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(1)
        
    for o, a in opts:
        if o in ('-h', '--help'):
            usage()
            sys.exit(0)
        else:
            print 'unknown arguments.'
            usage()
            sys.exit(2)
    
    test1()
    test2()
    
    sys.exit(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')
    
    main(sys.argv)
