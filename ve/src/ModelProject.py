#-*- coding:utf-8 -*-

'''
管理项目。
1, 必须创建一个项目，项目的配置放在~/.wside/project_name/project.conf 缺省目录。
2, 项目由一个wsproject.ini文件来标志。
3, 
'''

import os
import ConfigParser
from gi.repository import GObject, Gtk, Gdk, GtkSource

from VeUtils import *
from ModelTags import ModelGTags
from VeWordProvider import VeWordProvider

class ModelProject(object):
    '''
    config_path:string:配置文件的路径 project.conf，这个不写到配置文件中。
    prj_name:string:项目名字
    src_dirs:[string]:代码的路径数组
    
    prj_tags:IdeGTags:负责管理Tags文件，和进行分析。
    
    #没有实现。
    #prj_self_config:string:项目自己配置文件。 project.self.conf
    #open_file_paths:[string]:目前打开的文件的路径数组
    '''
    
    PROJECT_CONFIG_NAME = 'project.conf'
    '''
    格式：
    [info]
    project_name=xxxx
    [src_path]
    src_0=xxx
    src_1=xxx
    '''
    
    @staticmethod
    def create(prj_dir, prj_name, src_dirs):
        '''
        创建一个项目。
        prj_dir:string:项目的路径。
        prj_name:string:项目的名字。
        src_dirs:[string]:代码所在的目录。
        '''
        
        # 创建项目的文件夹
        #if not os.path.exists(prj_dir):
        #    os.mkdir(prj_dir)
        
        # 拼出配置文件的路径
        config_path = os.path.join(prj_dir, ModelProject.PROJECT_CONFIG_NAME)
        print '项目配置文件 %s' % config_path
        
        # 写入基本的信息
        prj = ModelProject()
        
        prj.config_path = config_path
        prj.prj_name = prj_name
        prj.src_dirs = src_dirs
        
        if prj.save():
            return prj
        else:
            return None
    
    @staticmethod
    def open(prj_dir):
        '''
        读取一个现存的项目
        '''
        if not os.path.exists(prj_dir):
            return None
        
        # 拼出配置文件的路径
        config_path = os.path.join(prj_dir, ModelProject.PROJECT_CONFIG_NAME)
        print '项目配置文件 %s' % config_path
        
        prj = ModelProject()
        
        if prj.read(config_path):
            return prj
        else:
            return None
        
    def __init__(self):
        ''' 初始化内部的属性 '''
        self.config_path = None
        self.prj_name = None
        self.src_dirs = []
        
        self.prj_tags = ModelGTags(self)
    
    def read(self, config_path):
        ''' 读取一个现存的配置文件
        return:Bool:是否正确读取。
        '''
        if not os.path.exists(config_path):
            return False
        
        cf = ConfigParser.ConfigParser()
        cf.read(config_path)
        
        self.config_path = config_path
        self.prj_name = None
        self.src_dirs = []
        
        for section in cf.sections():
            
            if section == 'info':
                prj_info = cf.items('info')
                print 'info:', prj_info
                self.prj_name = cf.get('info', 'project_name')
                    
            elif section == 'src_path':
                src_pathes = cf.items('src_path')
                print 'src_path:', src_pathes
                for src_path in src_pathes:
                    self.src_dirs.append(src_path[1])
        
        return True
    
    def save(self):
        '''
        保存当前的项目配置。
        return:Bool:是否成功。
        '''
        
        if is_empty(self.config_path):
            print '配置文件路径是空，无法保存。'
            return False
        
        if is_empty(self.prj_name):
            print '项目名字是空，无法保存。'
            return False
                
        if not os.path.exists(self.config_path):
            print 'config path:' + self.config_path
            basename = os.path.dirname(self.config_path)
            if not os.path.exists(basename):
                os.mkdir(basename)
            os.mknod(self.config_path)
        
        # 写入数据。
        cf = ConfigParser.ConfigParser()
        
        cf.add_section('info')
        cf.set('info', 'project_name', self.prj_name)
        
        cf.add_section('src_path')
        for n, src_path in enumerate(self.src_dirs):
            cf.set('src_path', 'src_' + str(n), src_path)
        
        fo_config = open(self.config_path, 'w')
        cf.write(fo_config)
        fo_config.close()
        
        return True
    
    def remove(self):
        '''
        删除当前的项目配置。
        return:Bool:是否成功。
        '''
        
        if is_empty(self.config_path):
            print '配置文件路径是空，无法保存。'
            return False
        
        if is_empty(self.prj_name):
            print '项目名字是空，无法保存。'
            return False
                
        if os.path.exists(self.config_path):
            print 'config path:' + self.config_path
            basename = os.path.dirname(self.config_path)
            os.remove(self.config_path)
            os.removedirs(basename)
        return True
    
    def prepare(self):
        ''' 进行预处理，在项目的配置打开后。'''
        ''' 如果Tag文件存在，则生成。如果已经存在，则更新。 '''
        
        return self.prj_tags.prepare()
    
    def query_tags_by_file(self, file_path):
        return self.prj_tags.query_tags_by_file(file_path)
    
    def query_defination_tags(self, name):
        return self.prj_tags.query_defination_tags(name)
    
    def query_reference_tags(self, name):
        return self.prj_tags.query_reference_tags(name)
    
    def get_completion_tags(self, prefix):
        ''' 根据前缀，查询到什么Tag符合要求。
        prefix string 前缀，比如“do_w”，查询符合条件[do_w.*]的tag名字。
        return [IdeOneTag] 包含名字的数组，如果没有符合的，就长度为空。
        '''
        return self.prj_tags.query_prefix_tags(prefix)
    
    def query_grep_tags(self, pattern, ignoreCase):
        return self.prj_tags.query_grep_tags(pattern, ignoreCase)
        
    def query_grep_filepath(self, pattern, ignoreCase=False):
        return self.prj_tags.query_grep_filepath(pattern, ignoreCase)
    
    def get_completion_provider(self):
        ''' 返回一个单词补全的提供者 '''
        return VeWordProvider(self)#self.prj_tags)
