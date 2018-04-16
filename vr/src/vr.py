#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os, sys, logging, getopt

class VSubject(object):
    def __init__(self):
        super(VSubject, self).__init__()
        self.observers = []
        
    def attach_observer(self, observer):
        if observer not in self.observers:
            self.observers.append(observer)
    
    def detach_observer(self, observer):
        if observer in self.observers:
            self.observers.remove(observer)
            
    def notify_observer(self):
        for observer in self.observers:
            observer._on_subject_update(self)
            
class VObserver(object):
    def __init__(self):
        super(VObserver, self).__init__()
        
    def _on_subject_update(self, subject):
        pass

class VObject(VSubject, VObserver):
    def __init__(self):
        super(VObject, self).__init__()
    
class VRelation(VObject):
    def __init__(self):
        super(VRelation, self).__init__()

class REqualValue(VRelation):
    
    def __init__(self):
        super(REqualValue, self).__init__()
        self.obj1 = None
        self.obj2 = None
        
    def constrain(self, obj1, obj2):
        if not isinstance(obj1, VValue) or not isinstance(obj2, VValue):
            logging.error("obj1 or obj1 is not VValue")
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
        
class VValue(VObject):
    def __init__(self, v):
        super(VValue, self).__init__()
        self.value = v
        
    def __str__(self, *args, **kwargs):
        return str(self.value)
    
    def set_value(self, v):
        if self.value != v:
            self.value = v
            self.notify_observer()
            
    def get_value(self):
        return self.value
        
def test():
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
    
    test()
    
    sys.exit(0)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s,%(levelname)s][%(funcName)s/%(filename)s:%(lineno)d]%(message)s')
    
    main(sys.argv)
