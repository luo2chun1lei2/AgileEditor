# -*- coding:utf-8 -*-

# 工作站模型。
# 负责整个工作站的工作，比如项目的添加、删除等，还包括配置文件和设定工作目录。

import os, string, logging
from ConfigParser import ConfigParser, NoSectionError, NoOptionError

from framework.FwUtils import *
from framework.FwComponent import FwComponent
from component.model.ModelProject import ModelProject

class ModelWorkshop(FwComponent):
    # 管理项目的工作区域。
    # 以 ws.conf 文件为核心。(ini文件)
    # 属性：
    #    ws_path:string:workshop的路径。
    #    ws_config_path:string:workshop的配置文件的路径。
    #    projects:[ModelProject]:所有项目。

    DEF_WS_PATH = ".ve"
    # 缺省Workshop的路径

    SEC_NAME_PRJ = 'projects'
    # Section name of project

    SEC_NAME_SETTING = 'setting'
    OPT_NAME_STYLE = 'style'
    OPT_NAME_FONT = 'font'

    def __init__(self, ws_path):
        # ws_path:string:workshop的路径。

        if is_empty(ws_path):
            logging.error('workshop路径不正确。%s' % (ws_path))
            ws_path = ModelWorkshop.DEF_WS_PATH

        # 设定Workshop的路径
        self.ws_path = ws_path

        # 如果文件夹不存在，则创建
        if not os.path.exists(self.ws_path):
            os.mkdir(self.ws_path)
            logging.error('创建了workshop:%s' % (self.ws_path))

        # 得到Workshop的配置文件
        self.ws_config_path = os.path.join(self.ws_path, 'ws.conf')

        # 如果配置文件不存在，则创建
        if not os.path.exists(self.ws_config_path):
            # 创建一个空的项目配置文件。
            self._create_conf(self.ws_config_path)
            logging.error('创建了Workshop配置文件:%s' % (self.ws_config_path))

        # 读取配置文件。
        self.setting, self.projects = self._read_conf(self.ws_config_path)

    # from component
    def onRegistered(self, manager):
        info = {'name':'model.workshop.getopt', 'help':'get one option value of workshop.'}
        manager.registerService(info, self)

        return True

    # from component
    def onRequested(self, manager, serviceName, params):
        if serviceName == "model.workshop.getopt":
            # get opt value by key.
            key = params['key']
            if key is None:
                logging.error("Need command arguments.")
                return (False, None)
            return (True, {'value': self.setting[key]})

        else:
            return (False, None)

    def get_project(self, project_name):
        # 根据项目名字，得到项目。
        # project_name:string:项目的名字
        # return:ModelProject:项目对象，如果没有找到，返回None

        for prj in self.projects:
            if prj.prj_name == project_name:
                return prj

        return None

    def find_project_by_src_path(self, path):
        # 根据路径，到每个项目的src路径中找，如果发现了就返回项目的名字。
        # return:string:如果没有找到，None

        for prj in self.projects:
            if path.startswith(prj.src_dirs[0]):
                return prj.prj_name
        return None

    def create_project(self, prj_name, prj_src_dirs):
        # 创建一个项目，并没有加入到workshop中。
        # prj_name:string:项目的名字。
        # src_dirs:[string]:代码所在的目录。
        # return:[ModelProject]:如果创建不成功，就返回None

        prj_path = os.path.join(self.ws_path, prj_name)
        prj = ModelProject.create(prj_path, prj_name, prj_src_dirs)

        return prj

    def add_project(self, project):
        # 添加一个项目到workshop中，并保存配置。
        self.projects.append(project)

        # 马上保存。
        self.save_conf()

    def del_project(self, project):
        # 从列表中删除一个项目，并保存配置，项目实际的配置没有删除。
        self.projects.remove(project)
        self.save_conf()

    def save_conf(self):
        # 保存当前的workshop的信息。
        self._write_conf(self.projects)

    def move_project_next(self, prj):
        # 将指定的项目向后移动
        # prj:ModelProject:

        found = self.projects.index(prj)
        if found < 0:
            return False
        elif found >= len(self.projects) - 1:
            return False

        self.projects[found] = self.projects[found + 1]
        self.projects[found + 1] = prj

        self.save_conf()
        return True

    def move_project_prev(self, prj):
        # 将执行的项目向前移动
        # prj:ModelProject:

        found = self.projects.index(prj)
        if found <= 0:
            return False
        elif found > len(self.projects) - 1:
            return False

        self.projects[found] = self.projects[found - 1]
        self.projects[found - 1] = prj

        self.save_conf()
        return True

    def _create_conf(self, config_path):
        # 生成缺省的配置文件。
        # 加入了一个[projects]

        # 创建解析器
        cf = ConfigParser()

        # 添加一个基本的节点
        cf.add_section(ModelWorkshop.SEC_NAME_PRJ)

        # 写入数据
        fo_config = open(self.ws_config_path, 'w+')
        cf.write(fo_config)
        fo_config.close()

    def _read_conf(self, config_path):
        # 读取workshop的配置文件

        # 创建解析器
        cf = ConfigParser()

        # 读取和分析数据
        cf.read(config_path)

        # 清空原来的项目组，然后读取配置文件中的项目组。
        prjs = []
        prj_infoes = cf.items(ModelWorkshop.SEC_NAME_PRJ)
        # print 'projects:', prj_infoes
        for prj_info in prj_infoes:
            prj_dir = os.path.join(self.ws_path, prj_info[1])  # 取后面的值
            prj = ModelProject.open(prj_dir)
            prjs.append(prj)

        # 获取 setting下面的设定项目。
        setting = {'style':'cobalt', 'font':'Ubuntu mono 12'}  # 缺省值
        try:
            setting[ModelWorkshop.OPT_NAME_STYLE] = cf.get(ModelWorkshop.SEC_NAME_SETTING, ModelWorkshop.OPT_NAME_STYLE)
        except (NoSectionError, NoOptionError):
            pass

        try:
            setting[ModelWorkshop.OPT_NAME_FONT] = cf.get(ModelWorkshop.SEC_NAME_SETTING, ModelWorkshop.OPT_NAME_FONT)
        except (NoSectionError, NoOptionError):
            pass

        return setting, prjs

    def _write_conf(self, projects):
        # 写入workshop的配置文件

        # 创建解析器
        cf = ConfigParser()

        # 添加 [projects]
        cf.add_section(ModelWorkshop.SEC_NAME_PRJ)
        # 写入每个项目的路径。
        for n, prj in enumerate(projects):
            # project<no> = basename(dir_path(project.config_path))
            cf.set(ModelWorkshop.SEC_NAME_PRJ,
                   "project" + str(n), os.path.basename(os.path.dirname(prj.config_path)))

        # setting的各种设置
        cf.add_section(ModelWorkshop.SEC_NAME_SETTING)
        cf.set(ModelWorkshop.SEC_NAME_SETTING, ModelWorkshop.OPT_NAME_STYLE,
                self.setting[ModelWorkshop.OPT_NAME_STYLE])
        cf.set(ModelWorkshop.SEC_NAME_SETTING, ModelWorkshop.OPT_NAME_FONT,
                self.setting[ModelWorkshop.OPT_NAME_FONT])

        # 写入数据
        fo_config = open(self.ws_config_path, 'w')
        cf.write(fo_config)
        fo_config.close()
