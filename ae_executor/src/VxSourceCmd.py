#-*- coding:utf-8 -*-

''' 记录命令和对应的结果。'''

class VxSourceCmd:
    
    def __init__(self, source, command):
        self.source = source
        self.command = command
        
class VxSourceCmdMng:
    
    my_instance = None
    
    def __init__(self):
        self.list = []
        
    @staticmethod
    def instance():
        if VxSourceCmdMng.my_instance is None:
            VxSourceCmdMng.my_instance = VxSourceCmdMng()
            
        return VxSourceCmdMng.my_instance
    
    @staticmethod
    def add_src_cmd(source, command):
        VxSourceCmdMng.instance().list.append(VxSourceCmd(source, command))
        
    @staticmethod
    def add(source_cmd):
        VxSourceCmdMng.instance().list.append(source_cmd)
        
    @staticmethod
    def last():
        l = VxSourceCmdMng.instance().list
        if len(l) == 0:
            return None
        else:
            return l[len(l) -1]
    
    @staticmethod
    def pop():
        l = VxSourceCmdMng.instance().list
        return l.pop()
    
    @staticmethod
    def clean():
        ''' 清除到只剩下最开始的。'''
        l = VxSourceCmdMng.instance().list
        if len(l) == 0:
            return
        
        while len(l) != 1:
            l.pop()
    
    @staticmethod
    def len():
        l = VxSourceCmdMng.instance().list
        return len(l)
    @staticmethod
    def pop_to(vx_source_cmd):
        l = VxSourceCmdMng.instance().list
        if len(l) == 0:
            return
        
        while l[len(l) -1] != vx_source_cmd:
            l.pop()