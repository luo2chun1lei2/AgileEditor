#-*- coding:utf-8 -*-

# 管理项目。
# 1, 根据配置文件显示项目。
# 2, 可以添加不同的路径。
# 3, 

import os, logging
import ConfigParser
from gi.repository import GObject, Gtk, Gdk, GtkSource

from VeUtils import *
from ModelTags import ModelGTags
from VeWordProvider import VeWordProvider

class ModelProject(object):
    # config_path:string:配置文件的路径 project.conf，这个不写到配置文件中。
    # prj_name:string:项目名字
    # src_dirs:[string]:代码的路径数组
    # prj_tags:ModelTags:负责管理Tags文件，和进行分析。
    
    #没有实现。
    #prj_self_config:string:项目自己配置文件。 project.self.conf
    #open_file_paths:[string]:目前打开的文件的路径数组
    
    PROJECT_CONFIG_NAME = 'project.conf'
    # 格式：
    # [info]
    # project_name=xxxx # TODO 没有必要！
    # [src_path]
    # src_0=xxx
    # src_1=xxx
    
    @staticmethod
    def create(prj_dir, prj_name, src_dirs):
        # 创建一个项目。
        # prj_dir:string:项目的路径。
        # prj_name:string:项目的名字。
        # src_dirs:[string]:代码所在的目录。
        # return:[ModelProject]:如果创建不成功，就返回None
        
        # 如果存在，就创建项目的文件夹
        if not os.path.exists(prj_dir):
            os.mkdir(prj_dir)
        
        # 拼出配置文件的路径
        config_path = os.path.join(prj_dir, ModelProject.PROJECT_CONFIG_NAME)
        logging.debug('create project config file:%s' % (config_path))
        
        # 设定项目的基本信息
        prj = ModelProject()
        
        prj.config_path = config_path
        prj.prj_name = prj_name
        prj.src_dirs = src_dirs
        
        # 写入基本的信息
        if prj.save():
            return prj
        else:
            return None
    
    @staticmethod
    def open(prj_dir):
        # 读取一个现存的项目
        # prj_dir:string:项目路径
        # return:ModelProject:错误，返回None。

        # 如果文件夹不存在，就返回错误
        if not os.path.exists(prj_dir):
            return None
        
        # 拼出配置文件的路径
        config_path = os.path.join(prj_dir, ModelProject.PROJECT_CONFIG_NAME)
        logging.debug('项目配置文件 %s' % (config_path))
        
        prj = ModelProject()
        
        # 读取配置文件信息
        if prj.read(config_path):
            return prj
        else:
            return None
        
    def __init__(self):
        # 初始化内部的属性
        
        self.config_path = None
        self.prj_name = None
        self.src_dirs = []
        
        self.prj_tags = ModelGTags(self)
    
    def read(self, config_path):
        # 读取一个现存的配置文件
        # config_path:string:配置文件的路径
        # return:Bool:是否正确读取。

        # 配置文件不存在，就返回错误
        if not os.path.exists(config_path):
            return False
        
        # 创建配置文件分析器
        cf = ConfigParser.ConfigParser()
        
        # 读取配置文件
        logging.debug('read project config:%s', (config_path))
        cf.read(config_path)
        
        # 初始化
        self.config_path = config_path
        self.prj_name = None
        self.src_dirs = []
        
        # 每个项目的值
        self.prj_name = cf.get('info', 'project_name')
        logging.debug('project name:%s', (self.prj_name))
        
        src_pathes = cf.items('src_path')
        logging.debug('project src_path:%s', (src_pathes))
        for src_path in src_pathes:
            self.src_dirs.append(src_path[1])

        return True
    
    def save(self):
        # 保存当前的项目配置。
        # return:Bool:是否成功。
        
        # 如果配置文件路径无效，就返回错误。
        if is_empty(self.config_path):
            logging.error('配置文件路径是空，无法保存。')
            return False
        
        if is_empty(self.prj_name):
            logging.error('项目名字是空，无法保存。')
            return False
                
        if not os.path.exists(self.config_path):
            logging.debug('create config path:%s' % (self.config_path))
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
        # 删除当前的项目配置。
        # return:Bool:是否成功。
        
        if is_empty(self.config_path):
            logging.error('配置文件路径是空，无法保存。')
            return False
        
        if is_empty(self.prj_name):
            logging.error('项目名字是空，无法保存。')
            return False
                
        if os.path.exists(self.config_path):
            logging.debug('remove config path:%s and project dir.' % self.config_path)
            basename = os.path.dirname(self.config_path)
            os.remove(self.config_path)
            os.removedirs(basename)
            
        return True
    
    ############################################################
    ## 下面是TAG的处理，因为以后如果src很多，那么就会有许多的TAG，所以Project做了隔离。
    ## TODO 以后制作项目组的概念，每个项目组包含一堆相关的项目，而项目只有一个src。
    
    def prepare(self):
        # 进行预处理，在项目的配置打开后。
        # 如果Tag文件存在，则生成。如果已经存在，则更新。
        
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
