#-*- coding:utf-8 -*-

'''
命令的模板
有些预先定义的命令，放在这里。
'''

class VcCmdTemplate:
    ''' 命令模板
    content string:命令，且是唯一标志
    desc string:命令的描述 
    '''
    def __init__(self, content, desc = ""):
        # 内容
        self.content = content
        # 描述
        self.desc = desc
    
    def get_content(self):
        return self.content
    
    def set_content(self, text):
        self.content = text
    
    def get_desc(self):
        return self.desc
    
    def set_desc(self, text):
        self.desc = text

class VcCmdTemplateMng:
    ''' 管理所有的命令模板 '''
    
    my_instance = None
    
    @staticmethod
    def instance():
        if VcCmdTemplateMng.my_instance is None:
            VcCmdTemplateMng.my_instance = VcCmdTemplateMng()
        
        return VcCmdTemplateMng.my_instance
    
    def __init__(self):
        self.list = []
        
        self._read_list()
    
    def add_cmd(self, content, description=""):
        for cmd in self.list:
            if cmd.content == content:
                print "遇到重复的命令 %s" % (content)
                return False
            
        cmd = VcCmdTemplate(content, description)
        self.list.append(cmd)

    def _find(self, key):
        for cmd in self.list:
            if cmd.key == key:
                return cmd
        return None
    
    @staticmethod
    def find(key):
        return VcCmdTemplateMng.instance()._find(key)
    
    def _read_list(self):
        ''' 目前由代码生成，以后修改成从文件中，或者实时分析得到结果。
        '''
        self.add_cmd("Customize");
        
        self.add_cmd("its_init");
        self.add_cmd("its_clean");
        self.add_cmd("its_make");
        self.add_cmd("its_install_dev");
        self.add_cmd("its_install_bin");
        
        self.add_cmd("soter_init");
        self.add_cmd("soter_git");
        self.add_cmd("soter_clean");
        self.add_cmd("soter_make");
        self.add_cmd("soter_install_dev");
        self.add_cmd("soter_install_bin");
