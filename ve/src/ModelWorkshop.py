#-*- coding:utf-8 -*-

'''
管理项目。
'''

import os, string
import ConfigParser
from gi.repository import Gtk, Gdk

from VeUtils import *
from ModelProject import ModelProject

class ModelWorkshop(object):
    '''
    管理项目的工作区域。
    以 ws.conf 文件为核心。(ini文件)
    属性：
        ws_path:string:workshop的路径。
        ws_config_path:string:workshop的配置文件的路径。
        projects:[ModelProject]:所有项目。
    '''
    
    SEC_NAME_PRJ = 'projects'
    
    def __init__(self, ws_path):
        '''
        ws_path:string:workshop的路径。
        '''
        
        if is_empty(ws_path):
            print 'ide的workshop路径不正确。%s' % ws_path
        
        self.ws_path = ws_path
        
        if not os.path.exists(self.ws_path):
            os.mkdir(self.ws_path)
            print '创建了workshop的路径。%s' % self.ws_path
            
        self.ws_config_path = os.path.join(self.ws_path, 'ws.conf')
        if not os.path.exists(self.ws_config_path):
            # 创建一个空的项目配置文件。
            self._create_conf(self.ws_config_path)  
        
        print 'workshop的路径：%s，配置文件:%s' % (self.ws_path, self.ws_config_path)
        
        # 读取配置文件。 
        self.projects =  self._read_conf(self.ws_config_path)
        
    def get_prj(self, project_name):
        for prj in self.projects:
            if prj.prj_name == project_name:
                return prj
            
        return None
        
    def add_project(self, project):
        ''' 添加一个项目。'''
        self.projects.append(project)
        
        # 马上保存。
        self.save_conf()
    
    def del_project(self, project):
        ''' 删除一个项目。 '''
        self.projects.remove(project)
        self.save_conf()
    
    def save_conf(self):
        ''' 保存当前的worshop的信息。'''
        self._write_conf(self.projects)
      
    def _create_conf(self, config_path):
        ''' 生成缺省的配置文件。
        加入了一个[projects] 
        ''' 
        cf = ConfigParser.ConfigParser()
        
        cf.add_section(ModelWorkshop.SEC_NAME_PRJ)
        
        fo_config = open(self.ws_config_path, 'w+')
        cf.write(fo_config)
        fo_config.close()
        
    def _read_conf(self, config_path):
        ''' 读取workshop的配置文件 '''
        
        cf = ConfigParser.ConfigParser()
        cf.read(config_path)
        
        prjs = []
        
        for section in cf.sections():
            
            if section == ModelWorkshop.SEC_NAME_PRJ:
                prj_infoes = cf.items(ModelWorkshop.SEC_NAME_PRJ)
                print 'projects:', prj_infoes
                for prj_info in prj_infoes:
                    prj_dir = prj_info[1]
                    prj = ModelProject.open(prj_dir)
                    prjs.append(prj)
        
        return prjs

    def _write_conf(self, projects):
        cf = ConfigParser.ConfigParser()
        
        cf.add_section(ModelWorkshop.SEC_NAME_PRJ)
        for n, prj in enumerate(projects):
            cf.set(ModelWorkshop.SEC_NAME_PRJ, "project" + str(n), \
                   os.path.dirname(prj.config_path) )
        
        fo_config = open(self.ws_config_path, 'w')
        cf.write(fo_config)
        fo_config.close()
