#-*- coding:utf-8 -*-

u'''
    Subject and Observer.
'''

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
            
    def notify_observers(self):
        for observer in self.observers:
            observer._on_subject_update(self)
            
class VObserver(object):
    def __init__(self):
        super(VObserver, self).__init__()
        
    def _on_subject_update(self, subject):
        # sub class implements this function.
        pass
