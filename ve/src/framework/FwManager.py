# -*- coding:utf-8 -*-
'''
框架的核心处理类
'''

import logging
from framework.FwBaseComponent import FwBaseComponent
from component.help.ViewHelp import ViewDialogInfo, VeiwDialogInfoFactory
from pkg_resources import _manager
from component.AppProcess import AppProcess
from component.AppView import AppView
from component.CommandParser import CommandParser

class FwService:
    def __init__(self, info, component):
        self.info = info
        self.component = component

class FwManager():

    # single instance
    _manager = None

    @staticmethod
    def instance(argv):
        if FwManager._manager is None:
            FwManager._manager = FwManager(argv)

        return FwManager._manager

    def __init__(self, argv):
        self.argv = argv
        
        # {<component type name>:string, <component factory instance>:FwComponentFactory}
        # 注意这里实际上保存的是具体的组件实例。
        self.components = {}
        
        # [服务和组件]: [<map>: <FwBaseComponent>]
        self.services = []

        # 注册已知的组件工厂。
        self.register("app_process", AppProcess())
        self.register("command_parser", CommandParser())
        self.register("app_view", AppView())
    
    def run(self):
        ''' 程序运行，整个系统不关闭，则此函数不关闭
        '''
        self.requestService("app.run", {'argv':self.argv})

    #######################################################
    ## 组件工厂相关函数

    def register(self, name, component):
        '''
        @param name: string: 工厂的名字，必须唯一
        @param componentFactory: FwComponentFactory: 工厂的实例
        '''
        self.components[name] = component
        component.init(self)

    def unregisterByName(self, componentName):
        '''
        @param factoryName: string: 工厂的名字
        '''
        del self.components[componentName]

    def findComponent(self, componentName):
        ''' 用名字查询工厂
        @param factoryName: string: 工厂的名字
        @return FwBaseComponnet: 找到的组件，None:没有找到。
        '''
        return self.components[componentName]
    
    #################################################
    ## 服务函数
    ## 服务参数必须包括
    ## "name": string: 服务的标志名字，建议用“xx.xx” 来表示。
    ##    如果名字匹配，就会调用此组件。
    ## "help": string: 显示帮助信息。

    def registerService(self, info, component):
        '''
        @param info: map: 服务的关键字加参数。
        '''
        self.services.append(FwService(info, component))
        return True

    def unregisterService(self, component):
        for service in self.services:
            if service.component is component:
                index = service.services.index(component)
                del self.services[index]
                break
        return True
            
    def requestService(self, serviceName, params):
        ''' 请求服务
        @param serviceName: string: 服务名称，必须和service的info的name相同。
        @param params: map: 传递给应答的组件
        @return (bool, map): (请求是否成功，返回数据) 
        '''
        for service in self.services:
            if service.info['name'] == serviceName:
                return service.component.dispatchService(self, serviceName, params)
                
        logging.error("cannot find service %s" % serviceName)
        return (False, None)
