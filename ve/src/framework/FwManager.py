# -*- coding:utf-8 -*-
'''
框架的核心处理类
'''

import logging

class FwService:
    def __init__(self, info, component):
        self.info = info
        self.component = component

class FwManager():
    ''' Framework的核心管理类。
    1，为了防止在加载组件的顺序问题，所以要求注册组件后才能申请服务，后面动态加载也是这样的流程。
      __init__ 中可以注册组件，组件在自己的 onRegistered 函数中注册自己的服务。
       然后当真正运行起来后，才能调用服务。
    2, 分成4个阶段：
    2.1，先将所有的组件放到框架中，可以注册自己的服务，但是不得调用任何服务。 <register>
    2.2，遍历所有的组件，允许其调用其他服务。这个跟一般的服务不同，这个是给所有的组件一个机会，让所有的组件在启动前相互交互。 <setup>
    2.3，正式开始组件的运转。 run
    2.4，程序结束前，遍历所有的组件，调用一个方法，给所有组件一个机会，处理所有结束工作，此时允许交互。 <teardown>
    2.5，程序结束时，遍历所有的组件，要求组件释放。 <unregister>.
    '''

    # single instance
    _manager = None

    @staticmethod
    def instance():
        if FwManager._manager is None:
            FwManager._manager = FwManager()

        return FwManager._manager

    def __init__(self):

        # {<component name>:string, <component instance>:FwComponent}
        self.components = {}

        # [服务的信息]: [<FwService>]
        self.services = []

        # 注册已知的组件工厂。
        # TODO 以后修改成从固定文件夹等搜索组件，然后加载。
        from component.AppProcess import AppProcess
        from component.AppView import AppView
        from component.AppArgs import AppArgs
        from component.help.ViewDailogInfo import ViewDialogInfo
        from component.help.ViewDialogCommon import ViewDialogCommon
        from component.help.ViewDialogProject import ViewDialogProject
        from component.help.ViewDialogProjectSetting import ViewDialogProjectSetting

        self._register("app_process", AppProcess())
        self._register("command_parser", AppArgs())
        self._register("app_view", AppView())
        self._register("dialog_info", ViewDialogInfo())
        self._register("dialog_common", ViewDialogCommon())
        self._register("dialog_project", ViewDialogProject())
        self._register("dialog_project_setting", ViewDialogProjectSetting())

    def run(self, argv):
        ''' 程序运行，整个系统不关闭，则此函数不关闭
        '''

        # 前期准备
        for (name, component) in self.components.items():
            if not component.onSetup(self):
                logging.error("Cannot prepare component(%s)", name)
                return False

        # 开始运行
        self.requestService("app.run", {'argv':argv})

        # 后期收尾
        for (name, component) in self.components.items():
            if not component.onTeardown(self):
                logging.error("Cannot closeout component(%s)", name)
                return False

        return True

    #######################################################
    # # 组件工厂相关函数

    def _register(self, name, component):
        ''' 注册组件，外部不要调用
        @param name: string: 工厂的名字，必须唯一
        @param componentFactory: FwComponentFactory: 工厂的实例
        '''
        self.components[name] = component
        component.onRegistered(self)
        return True

    def load(self, name, component):
        ''' 外部使用的，加载一个组件：注册、初始化、通知其他组件都初始化
        '''
        if not self._register(name, component):
            return False

        if not component.onSetup(self):
            return False

        for oneName, oneComponent in self.components.items():
            if name != oneName:
                if not oneComponent.onSetup(self):
                    return False
        return True

    def unregisterByName(self, componentName):
        '''
        @param factoryName: string: 工厂的名字
        '''
        component = self.components[componentName]
        if component is None:
            logging.error("Cannot find component(%s)" % componentName)
            return False

        component.onUnregistered()
        del self.components[componentName]

        return True

    def findComponent(self, componentName):
        ''' 用名字查询工厂
        @param factoryName: string: 工厂的名字
        @return FwBaseComponnet: 找到的组件，None:没有找到。
        '''
        return self.components[componentName]

    #################################################
    # # 服务函数
    # # 服务参数必须包括
    # # "name": string: 服务的标志名字，建议用“xx.xx” 来表示。
    # #    如果名字匹配，就会调用此组件。
    # # "help": string: 显示帮助信息。

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
                return service.component.onRequested(self, serviceName, params)

        logging.error("cannot find service %s" % serviceName)
        return (False, None)

    #############################################
    # for DEBUG
    def showComponents(self, needStr=False):
        ''' 显示目前的组件信息
        '''
        text = "components:\n"
        for name, cmpt in self.components.items():
            text += "\t%s : %s\n" % (name, type(cmpt).__module__)

        if needStr:
            return text
        else:
            print text
            return None

    def showServices(self, needStr=False):
        ''' 显示目前注册的服务信息。
        '''

        text = "services:\n"
        for service in self.services:
            info = service.info
            text += "\t%s : %s\n" % (info['name'], info['help'])

        if needStr:
            return text
        else:
            print text
            return None
